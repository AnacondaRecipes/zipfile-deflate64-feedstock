/* Decode a raw Deflate64 stream through libinfback9-resumable, feeding it in
 * fixed-size chunks the way zipfile-deflate64's wrapper does.
 *
 * usage: test_infback9 <file> <chunk_size>    (chunk_size 0 = whole file)
 * prints: <decoded_len> <fnv1a64 hex> <last_rc>
 * exit:   0 when the stream ended (Z_STREAM_END), 1 otherwise, 2 on usage/IO error
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "infback9r.h"

/* The library requires a zero-initializing allocator (see infback9r.h). */
static voidpf zalloc_zero(voidpf opaque, uInt items, uInt size) {
    (void)opaque;
    return calloc(items, size);
}
static void zfree_std(voidpf opaque, voidpf p) {
    (void)opaque;
    free(p);
}

typedef struct { unsigned long long len; unsigned long long hash; } sink_t;

static unsigned in_none(void *desc, z_const unsigned char **buf) {
    (void)desc; (void)buf;
    return 0; /* input is supplied through next_in/avail_in before each call */
}
static int out_sink(void *desc, unsigned char *buf, unsigned len) {
    sink_t *s = (sink_t *)desc;
    for (unsigned i = 0; i < len; i++) {
        s->hash ^= buf[i];
        s->hash *= 1099511628211ULL;
    }
    s->len += len;
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: %s <file> <chunk_size>\n", argv[0]); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *data = malloc(n > 0 ? (size_t)n : 1);
    if (!data || fread(data, 1, (size_t)n, f) != (size_t)n) { fclose(f); return 2; }
    fclose(f);
    size_t chunk = (size_t)strtoul(argv[2], NULL, 10);
    if (chunk == 0) chunk = (size_t)n;

    z_stream strm;
    memset(&strm, 0, sizeof strm);
    strm.zalloc = zalloc_zero;
    strm.zfree = zfree_std;
    unsigned char *window = calloc(1, 1u << 16); /* infback9 needs exactly 64 KiB */
    if (inflateBack9Init(&strm, window) != Z_OK) { fprintf(stderr, "init failed\n"); return 2; }

    sink_t sink = { 0, 1469598103934665603ULL };
    int rc = Z_BUF_ERROR;
    size_t off = 0;
    while (off < (size_t)n) {
        size_t take = ((size_t)n - off < chunk) ? (size_t)n - off : chunk;
        strm.next_in = data + off;
        strm.avail_in = (uInt)take;
        rc = inflateBack9(&strm, in_none, NULL, out_sink, &sink);
        off += take;
        if (rc == Z_STREAM_END) break;
        if (rc == Z_BUF_ERROR && strm.next_in == Z_NULL) continue; /* needs more input */
        break; /* data/stream error */
    }
    inflateBack9End(&strm);
    printf("%llu %016llx %d\n", sink.len, sink.hash, rc);
    free(window);
    free(data);
    return rc == Z_STREAM_END ? 0 : 1;
}
