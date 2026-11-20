"""Prints the README's code block that follows "<!-- NAME -->", exactly as printed:
    python tests/readme.py "example: pdfkit"
"""
import re
import sys
from pathlib import Path

readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
marker = f"<!-- {sys.argv[1]} -->"
at = readme.find(marker)
m = re.match(r"\s*```[a-z]*\n(.*?)\n```", readme[at + len(marker):], re.S) if at >= 0 else None
if not m:
    sys.exit(f"README.md has no code block after {marker}")
print(m.group(1))
