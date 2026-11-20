#!/usr/bin/env python3
"""Builds the wheels of one release of marqius-wkhtmltopdf, one per platform.

    python3 build.py VERSION BUILDS OUT

BUILDS holds the release's builds, checked by `.github/release.py fetch` (its SHA256SUMS is checked
again here). Each wheel carries the build for its platform, the marqius_wkhtmltopdf module and the
`marqius-wkhtmltopdf` command. The Linux builds are static, so each Linux wheel serves glibc and musl
alike. The wheels are reproducible: the same builds make the same files. Only the standard library
is used.
"""
import base64
import hashlib
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAME = "marqius-wkhtmltopdf"
MODULE = "marqius_wkhtmltopdf"
# build on marqius.com -> wheel platform tags
TAGS = {
    "linux-x86_64": ["manylinux_2_12_x86_64", "manylinux2010_x86_64", "musllinux_1_1_x86_64"],
    "linux-arm64": ["manylinux_2_17_aarch64", "manylinux2014_aarch64", "musllinux_1_1_aarch64"],
    "macos-arm64": ["macosx_11_0_arm64"],
    "windows-x86_64.exe": ["win_amd64"],
}
STAMP = (2026, 1, 1, 0, 0, 0)  # every file's date in the wheel, so that wheels are reproducible

# Unix: a few lines of sh start the program under the names libraries run
LAUNCHER = """#!/bin/sh
# Runs marqius-wkhtmltopdf as {name}, for libraries given this file's path. pip does not put it on
# the PATH. marqius-wkhtmltopdf is commercial software with a 30-day free trial: marqius.com/wkhtmltopdf
self=$0
while [ -h "$self" ]; do
    link=$(readlink "$self")
    case $link in /*) self=$link ;; *) self=${{self%/*}}/$link ;; esac
done
case $self in */*) here=${{self%/*}} ;; *) here=. ;; esac
exec "$here/marqius-wkhtmltopdf" {name} "$@"
"""

SUMMARY = ("marqius-wkhtmltopdf, the maintained drop-in replacement for wkhtmltopdf, for python-pdfkit, "
           "django-wkhtmltopdf and imgkit (commercial, 30-day trial)")


def metadata(version):
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    head = f"""Metadata-Version: 2.4
Name: {NAME}
Version: {version}
Summary: {SUMMARY}
Author-email: Simple AI LLC <hello@marqius.com>
License-Expression: LicenseRef-marqius-wkhtmltopdf
License-File: LICENSE.md
Project-URL: Homepage, https://marqius.com/wkhtmltopdf/
Project-URL: Documentation, https://marqius.com/download/developer-manual.pdf
Project-URL: Source, https://github.com/marqiushq/marqius-wkhtmltopdf-python
Project-URL: Licences, https://marqius.com/licence/marqius-wkhtmltopdf
Keywords: wkhtmltopdf,wkhtmltoimage,pdf,html-to-pdf,pdfkit,django-wkhtmltopdf,imgkit
Classifier: Development Status :: 5 - Production/Stable
Classifier: Intended Audience :: Developers
Classifier: Operating System :: MacOS
Classifier: Operating System :: Microsoft :: Windows
Classifier: Operating System :: POSIX :: Linux
Classifier: Programming Language :: Python :: 3
Classifier: Topic :: Printing
Classifier: Topic :: Text Processing :: Markup :: HTML
Requires-Python: >=3.8
Description-Content-Type: text/markdown

"""
    return head + readme


def record_hash(data):
    return "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()


def wheel(version, build, program, out):
    tags = TAGS[build]
    windows = build.startswith("windows")
    dist_info = f"{MODULE}-{version}.dist-info"
    files = []  # (path in the wheel, bytes, executable)
    init = (HERE / MODULE / "__init__.py").read_text(encoding="utf-8")
    init, n = re.subn(r'^__version__ = "[^"]*"$', f'__version__ = "{version}"', init, flags=re.M)
    if n != 1:
        sys.exit(f"{MODULE}/__init__.py has no single __version__ line")
    files.append((f"{MODULE}/__init__.py", init.encode(), False))
    for name in ("__main__.py", "py.typed"):
        files.append((f"{MODULE}/{name}", (HERE / MODULE / name).read_bytes(), False))
    files.append((f"{MODULE}/bin/marqius-wkhtmltopdf" + (".exe" if windows else ""), program, True))
    if not windows:
        for name in ("wkhtmltopdf", "wkhtmltoimage"):
            files.append((f"{MODULE}/bin/{name}", LAUNCHER.format(name=name).encode(), True))
    files.append((f"{dist_info}/METADATA", metadata(version).encode("utf-8"), False))
    files.append((f"{dist_info}/WHEEL", ("Wheel-Version: 1.0\nGenerator: marqius-wkhtmltopdf build.py\n"
                                         "Root-Is-Purelib: false\n"
                                         + "".join(f"Tag: py3-none-{t}\n" for t in tags)).encode(), False))
    files.append((f"{dist_info}/entry_points.txt",
                  b"[console_scripts]\nmarqius-wkhtmltopdf = marqius_wkhtmltopdf.__main__:main\n", False))
    files.append((f"{dist_info}/licenses/LICENSE.md", (HERE / "LICENSE.md").read_bytes(), False))
    record = "".join(f"{path},{record_hash(data)},{len(data)}\n" for path, data, _ in files)
    files.append((f"{dist_info}/RECORD", (record + f"{dist_info}/RECORD,,\n").encode(), False))

    path = out / f"{MODULE}-{version}-py3-none-{'.'.join(tags)}.whl"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data, executable in files:
            info = zipfile.ZipInfo(name, STAMP)
            info.create_system = 3  # Unix, so that the file modes below are read
            info.external_attr = (0o100755 if executable else 0o100644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data, compresslevel=9)
    return path


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    version, builds, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    sums = dict(reversed(line.split()) for line in (builds / "SHA256SUMS").read_text().splitlines())
    out.mkdir(parents=True, exist_ok=True)
    for build in TAGS:
        src = builds / f"marqius-wkhtmltopdf-{build}"
        program = src.read_bytes()
        if sums.get(src.name) != hashlib.sha256(program).hexdigest():
            sys.exit(f"{src} does not match SHA256SUMS")
        made = wheel(version, build, program, out)
        print(f"{made.name} ({made.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
