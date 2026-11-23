"""Prints the README's code block that follows "<!-- NAME -->", exactly as printed:
    python tests/readme.py "example: pdfkit"
With --inline, prints instead each `code` of the paragraph that follows the marker, one a line:
    python tests/readme.py --inline "quickstart: windows"
"""
import re
import sys
from pathlib import Path

args = sys.argv[1:]
inline = args[:1] == ["--inline"]
if inline:
    args = args[1:]
readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
marker = f"<!-- {args[0]} -->"
at = readme.find(marker)
rest = readme[at + len(marker):] if at >= 0 else ""
if inline:
    paragraph = rest.lstrip("\n").split("\n\n", 1)[0]
    codes = re.findall(r"`([^`]+)`", paragraph)
    if at < 0 or not codes:
        sys.exit(f"README.md has no paragraph with code after {marker}")
    sys.stdout.buffer.write(("\n".join(codes) + "\n").encode("utf-8"))
    sys.exit(0)
m = re.match(r"\s*```[a-z]*\n(.*?)\n```", rest, re.S)
if not m:
    sys.exit(f"README.md has no code block after {marker}")
sys.stdout.buffer.write((m.group(1) + "\n").encode("utf-8"))
