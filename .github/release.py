#!/usr/bin/env python3
"""Follows the releases of marqius-wkhtmltopdf for a package that carries it.

    python3 .github/release.py latest              prints the latest release's version
    python3 .github/release.py newer A B           succeeds when version A is newer than version B
    python3 .github/release.py fetch VERSION DIR   each build of VERSION, checked against its published SHA-256

`fetch` downloads every build of VERSION into DIR, checks each against the SHA-256 published beside
it, and writes DIR/SHA256SUMS; it stops at the first build that does not match. MARQIUS_DOWNLOAD
names another place to download from (a mirror, or file:// for tests). Only the standard library is
used.
"""
import hashlib
import os
import re
import sys
import urllib.request
from pathlib import Path

BASE = os.environ.get("MARQIUS_DOWNLOAD", "https://marqius.com/download/marqius-wkhtmltopdf").rstrip("/")
BUILDS = ["linux-x86_64", "linux-arm64", "macos-arm64", "windows-x86_64.exe"]
AGENT = "marqiushq-package-release (+https://github.com/marqiushq)"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def version(v):
    if not re.fullmatch(r"\d+(\.\d+)+", v):
        sys.exit(f"not a version: {v[:40]!r}")
    return tuple(int(x) for x in v.split("."))


def latest():
    v = fetch(f"{BASE}/latest").decode("utf-8").strip()
    version(v)
    print(v)


def fetch_all(v, folder):
    version(v)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    sums = []
    for build in BUILDS:
        name = f"marqius-wkhtmltopdf-{build}"
        url = f"{BASE}/{v}/{name}"
        published = fetch(f"{url}.sha256").decode("utf-8").strip()[:64].lower()
        if not re.fullmatch(r"[0-9a-f]{64}", published):
            sys.exit(f"{url}.sha256 does not hold a checksum")
        data = fetch(url)
        got = hashlib.sha256(data).hexdigest()
        if got != published:
            sys.exit(f"{url} does not match its published SHA-256 ({published}; it has {got})")
        (folder / name).write_bytes(data)
        os.chmod(folder / name, 0o755)
        sums.append(f"{published}  {name}\n")
        print(f"{name} {v}: {published}")
    (folder / "SHA256SUMS").write_text("".join(sums), encoding="utf-8")


def main():
    a = sys.argv[1:]
    if a == ["latest"]:
        latest()
    elif len(a) == 3 and a[0] == "newer":
        sys.exit(0 if version(a[1]) > version(a[2]) else 1)
    elif len(a) == 3 and a[0] == "fetch":
        fetch_all(a[1], a[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
