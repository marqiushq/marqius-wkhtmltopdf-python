"""marqius-wkhtmltopdf under its own name: the `marqius-wkhtmltopdf` command this package installs,
or `python -m marqius_wkhtmltopdf`: help, licence, compare, install and wkhtmltopdf's command line."""
import os
import subprocess
import sys

from . import program


def main():
    exe = program()
    args = [exe] + sys.argv[1:]
    if os.name == "posix":
        os.execv(exe, args)  # the program takes this process's place
    sys.exit(subprocess.call(args))


if __name__ == "__main__":
    main()
