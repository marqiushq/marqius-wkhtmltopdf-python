"""marqius-wkhtmltopdf for Python's wkhtmltopdf libraries.

`path()` gives the installed program's path, to give python-pdfkit, django-wkhtmltopdf or another
library that runs wkhtmltopdf, where it asks for the program::

    import pdfkit, marqius_wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf=marqius_wkhtmltopdf.path())

`image_path()` is the same for wkhtmltoimage (imgkit). The wheel pip installs carries the program for
its platform. marqius-wkhtmltopdf is commercial software from Simple AI LLC, with a 30-day free
trial: https://marqius.com/licence/marqius-wkhtmltopdf
"""
import os
import shutil
import sys
import tempfile

__version__ = "0.12.13.1"
__all__ = ["path", "image_path", "program", "__version__"]

_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
_WINDOWS = sys.platform == "win32"


def path() -> str:
    """The installed program's path, as wkhtmltopdf: give it where a library asks for wkhtmltopdf."""
    return _named("wkhtmltopdf")


def image_path() -> str:
    """Its path as wkhtmltoimage, for pictures (imgkit, for instance)."""
    return _named("wkhtmltoimage")


def program() -> str:
    """The program under its own name, marqius-wkhtmltopdf: help, licence, compare and install."""
    return _runnable(os.path.join(_BIN, "marqius-wkhtmltopdf.exe" if _WINDOWS else "marqius-wkhtmltopdf"))


def _runnable(file: str) -> str:
    # an installer that dropped the wheel's file modes: give them back where the folder allows
    if not _WINDOWS and os.path.isfile(file) and not os.access(file, os.X_OK):
        try:
            os.chmod(file, 0o755)
        except OSError:
            pass
    return file


def _named(name: str) -> str:
    """The path that starts the program as `name`: a few lines of sh in the package; on Windows, a
    hard link beside the program (a copy where links cannot be made)."""
    if not _WINDOWS:
        program()
        return _runnable(os.path.join(_BIN, name))
    exe = program()
    size = os.path.getsize(exe)
    for place in (_BIN, os.path.join(tempfile.gettempdir(), "marqius-wkhtmltopdf-" + __version__)):
        to = os.path.join(place, name + ".exe")
        try:
            if os.path.getsize(to) == size:
                return to
        except OSError:
            pass
        try:
            os.makedirs(place, exist_ok=True)
            try:
                os.remove(to)
            except OSError:
                pass
            try:
                os.link(exe, to)
            except OSError:
                shutil.copyfile(exe, to)
            return to
        except OSError:
            continue
    raise RuntimeError("marqius-wkhtmltopdf cannot be given the name %s.exe: neither %s nor %s can be written"
                       % (name, _BIN, tempfile.gettempdir()))
