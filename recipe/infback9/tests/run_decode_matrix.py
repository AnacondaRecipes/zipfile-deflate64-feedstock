"""Build-time check of libinfback9-resumable: decode the upstream Deflate64
fixtures with test_infback9, feeding each one in several chunk sizes. Every
chunk size must give the same output and end the stream; a truncated stream
must stop without ending it.

usage: python run_decode_matrix.py <test_infback9 executable> <fixture dir>
"""
import pathlib
import subprocess
import sys
import tempfile

FIXTURES = ["10_lines", "100_lines", "10k_lines", "100k_lines"]
CHUNKS = [1, 2, 3, 7, 31, 4096, 65536, 0]  # 0 = whole file
EXPECTED_LEN = {"100k_lines": 2188890}


def run(exe, path, chunk):
    r = subprocess.run([exe, str(path), str(chunk)], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def main(exe, fixture_dir):
    fixture_dir = pathlib.Path(fixture_dir)
    for name in FIXTURES:
        path = fixture_dir / f"zd64-{name}.deflate64"
        results = set()
        for chunk in CHUNKS:
            rc, out = run(exe, path, chunk)
            if rc != 0:
                sys.exit(f"{name} chunk={chunk}: stream did not end ({out!r})")
            results.add(out)
        if len(results) != 1:
            sys.exit(f"{name}: chunk sizes disagree: {sorted(results)}")
        length = int(results.pop().split()[0])
        if name in EXPECTED_LEN and length != EXPECTED_LEN[name]:
            sys.exit(f"{name}: decoded {length} bytes, expected {EXPECTED_LEN[name]}")
        print(f"{name}: {length} bytes, {len(CHUNKS)} chunk sizes agree")

    data = (fixture_dir / "zd64-100k_lines.deflate64").read_bytes()[:1000]
    with tempfile.TemporaryDirectory() as tmp:
        truncated = pathlib.Path(tmp) / "truncated.deflate64"
        truncated.write_bytes(data)
        rc, out = run(exe, truncated, 0)
    if rc != 1 or not out.endswith(" -5"):
        sys.exit(f"truncated stream: expected rc=1 and Z_BUF_ERROR, got rc={rc} {out!r}")
    print("truncated stream: stops with Z_BUF_ERROR")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
