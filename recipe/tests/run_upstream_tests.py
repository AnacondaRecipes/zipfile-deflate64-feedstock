"""Run upstream zipfile-deflate64's test suite against the installed package.

The upstream archive carries Git LFS pointer files in tests/data; the real
fixtures come from sha256-pinned recipe sources (fixture-downloads/zd64-*),
copied over the pointers here under their original names.
"""
import pathlib
import shutil
import subprocess
import sys

here = pathlib.Path.cwd()
data_dir = here / "upstream-tests" / "tests" / "data"
for blob in sorted((here / "fixture-downloads").glob("zd64-*")):
    name = blob.name[len("zd64-"):]
    if name.endswith(".zip.fixture"):
        name = name[: -len(".fixture")]
    shutil.copyfile(blob, data_dir / name)
    print(f"fixture {name}: {blob.stat().st_size} bytes")

sys.exit(subprocess.call(
    [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "upstream-tests/tests"]))
