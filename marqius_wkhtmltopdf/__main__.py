"""marqius-wkhtmltopdf under its own name: the `marqius-wkhtmltopdf` command this package installs,
or `python -m marqius_wkhtmltopdf`: help, licence, compare, install and wkhtmltopdf's command line.

`marqius-wkhtmltopdf update` updates this package itself, in the Python it runs in: with pip, or
with uv when uv installed it."""
import os
import shutil
import site
import subprocess
import sys
from importlib import metadata, util
from typing import List, Optional

from . import __version__, program

NAME = "marqius-wkhtmltopdf"


def installed_version() -> Optional[str]:
    """The version installed now, read by a new Python: this one still has the old one loaded."""
    run = subprocess.run([sys.executable, "-c", f"import importlib.metadata as m; print(m.version({NAME!r}))"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
    if run.returncode != 0 or not run.stdout.strip():
        return None
    return run.stdout.strip()


def installer() -> str:
    """What installed this package: pip, uv, poetry, ... ("" when it did not say)."""
    try:
        return (metadata.distribution(NAME).read_text("INSTALLER") or "").strip().lower()
    except Exception:
        return ""


def in_user_site() -> bool:
    """Installed with pip install --user, so updated the same way."""
    try:
        return bool(site.ENABLE_USER_SITE) and os.path.abspath(__file__).startswith(
            os.path.abspath(site.getusersitepackages()) + os.sep)
    except Exception:
        return False


def running_from_command() -> bool:
    """On Windows, `marqius-wkhtmltopdf update` runs from the command's own .exe in Scripts, which
    Windows lets nobody move or replace while it runs: pip could not update the package from there."""
    if os.name != "nt":
        return False
    exe = os.path.abspath(sys.argv[0])
    if not exe.lower().endswith(".exe"):
        exe += ".exe"  # (pip's script for the command takes .exe off sys.argv[0])
    return os.path.basename(exe).lower() == NAME + ".exe" and os.path.isfile(exe)


def update() -> int:
    """Installs the newest version of this package in the Python it runs in; says what it did."""
    if running_from_command():
        print(f"On Windows, the {NAME} command cannot replace itself while it runs. Run this instead:\n\n"
              f"    python -m marqius_wkhtmltopdf update", file=sys.stderr)
        return 1
    by = installer()
    command: List[str]
    if by == "uv":
        uv = shutil.which("uv")
        if not uv:
            print(f"{NAME} was installed with uv, which is not on the PATH. Update it with:\n\n"
                  f"    uv pip install --upgrade {NAME}", file=sys.stderr)
            return 1
        command = [uv, "pip", "install", "--upgrade", "--python", sys.executable, NAME]
        shown = f"uv pip install --upgrade {NAME}"
    elif by in ("", "pip"):
        if util.find_spec("pip") is None:
            print(f"This Python has no pip. Update {NAME} the way you installed it, for example:\n\n"
                  f"    uv pip install --upgrade {NAME}", file=sys.stderr)
            return 1
        user = ["--user"] if in_user_site() else []
        command = [sys.executable, "-m", "pip", "install", "--upgrade", "--disable-pip-version-check"] + user + [NAME]
        shown = "pip install --upgrade " + " ".join(user + [NAME])
    else:
        # poetry, pdm, conda...: the project's own tool keeps its lock file; pip here would not
        print(f"{NAME} was installed with {by}. Update it with {by}, so that your project's lock file "
              f"follows, for example:\n\n    {by} update {NAME}", file=sys.stderr)
        return 1
    print(f"{NAME} {__version__}: looking for a newer version ({shown})", flush=True)
    code = subprocess.call(command)
    if code != 0:
        print(f"{NAME} was not updated: {shown} failed.", file=sys.stderr)
        return code
    now = installed_version()
    if now == __version__:
        print(f"{NAME} {__version__} is the newest version.")
    else:
        print(f"{NAME} is now {now}.")
        print(f"If your requirements pin {NAME} to a version, change it there too.")
    return 0


def main() -> None:
    if sys.argv[1:] == ["update"]:
        sys.exit(update())
    exe = program()
    args = [exe] + sys.argv[1:]
    if os.name == "posix":
        os.execv(exe, args)  # the program takes this process's place
    sys.exit(subprocess.call(args))


if __name__ == "__main__":
    main()
