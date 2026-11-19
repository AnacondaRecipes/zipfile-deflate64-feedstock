/* infback9r.h -- public header of libinfback9-resumable (conda packaging).
 *
 * The library is zlib 1.4 contrib/infback9 (Deflate64 decoder) plus the
 * cielavenir/zlib "made infback9 resumable" commit, with its three entry
 * points renamed so they never collide with a stock inflateBack9 that a libz
 * might export. Callers keep the stock spelling; these defines map it.
 *
 * Requirement: supply a zero-initializing strm->zalloc (and the paired
 * strm->zfree). inflateBack9Init does not initialize the saved resume state;
 * zlib's default allocator (malloc) is not supported. zipfile-deflate64
 * meets this by allocating with PyMem_Calloc.
 */
#ifndef INFBACK9R_H
#define INFBACK9R_H

#include "zlib.h"

#define inflateBack9Init_ infback9r_init_
#define inflateBack9      infback9r_decode
#define inflateBack9End   infback9r_end

#include "infback9.h"

#endif /* INFBACK9R_H */
