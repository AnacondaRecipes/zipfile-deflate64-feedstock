"""Check that libinfback9-resumable exports exactly its 3 renamed entry points.

usage: python check_exports.py <path to the shared library>
Exits 0 when the allowlist holds, 1 otherwise.
"""
import ctypes
import sys

MUST_EXPORT = ["infback9r_init_", "infback9r_decode", "infback9r_end"]
# Stock names (would collide with a libz built with ZLIB_WITH_INFBACK9) and
# zlib internals compiled privately into the library: none may be visible.
MUST_HIDE = [
    "inflateBack9", "inflateBack9Init_", "inflateBack9End",
    "zlibVersion", "zlibCompileFlags", "zError",
    "zcalloc", "zcfree", "inflate_table9", "z_errmsg",
]


def main(path):
    lib = ctypes.CDLL(path)
    bad = []
    for name in MUST_EXPORT:
        if not hasattr(lib, name):
            bad.append(f"missing export: {name}")
    for name in MUST_HIDE:
        if hasattr(lib, name):
            bad.append(f"unexpected export: {name}")
    for line in bad:
        print(line)
    print("OK" if not bad else f"FAIL ({len(bad)})")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
