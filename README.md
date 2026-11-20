# marqius-wkhtmltopdf for Python

**marqius-wkhtmltopdf** is the maintained drop-in replacement for wkhtmltopdf. This package brings it to your project for python-pdfkit, django-wkhtmltopdf and imgkit: keep your library, your HTML templates and your PDF calls, and point the library at it with one line. It runs on Linux (x86-64 and ARM64, glibc and musl), Apple silicon Macs and Windows (x86-64), and needs no X server, Qt or system libraries.

<!-- install -->
```bash
pip install marqius-wkhtmltopdf
```

pip installs the wheel for your platform, which carries the program itself: nothing is downloaded when your code runs.

On a server or in a container without fonts, such as a slim or Alpine image, the program says so and prints the one line that installs them for that system.

## Point your library at it

`marqius_wkhtmltopdf.path()` gives the installed program's path: give it to your library where it asks for wkhtmltopdf, and `marqius_wkhtmltopdf.image_path()` where it asks for wkhtmltoimage. Each is a path inside your environment's `site-packages`; nothing is installed under the name `wkhtmltopdf` on your system.

### python-pdfkit

Where your code has `import pdfkit, marqius_wkhtmltopdf`:

<!-- example: pdfkit -->
```python
config = pdfkit.configuration(wkhtmltopdf=marqius_wkhtmltopdf.path())
pdfkit.from_string("<h1>Invoice 42</h1>", "invoice.pdf", configuration=config)
```

### django-wkhtmltopdf

In your project's `settings.py`:

<!-- example: django-wkhtmltopdf settings.py -->
```python
import marqius_wkhtmltopdf, shlex
WKHTMLTOPDF_CMD = shlex.quote(marqius_wkhtmltopdf.path())
```

django-wkhtmltopdf reads `WKHTMLTOPDF_CMD` as a command line, so the path is quoted. Your `PDFTemplateView` and `PDFTemplateResponse` views then make PDFs as before.

### imgkit

Where your code has `import imgkit, marqius_wkhtmltopdf`:

<!-- example: imgkit -->
```python
config = imgkit.config(wkhtmltoimage=marqius_wkhtmltopdf.image_path())
imgkit.from_string("<h1>Invoice 42</h1>", "invoice.jpg", config=config)
```

## The program itself

Installing the package also installs the command `marqius-wkhtmltopdf`: `marqius-wkhtmltopdf help python-pdfkit` shows each library's setting, `marqius-wkhtmltopdf compare old.pdf new.pdf` lists every difference between a PDF made by wkhtmltopdf and one made by marqius-wkhtmltopdf, and `marqius-wkhtmltopdf licence` shows the trial days left.

To give it the names `wkhtmltopdf` and `wkhtmltoimage` for everything on a server, as the [one-line installer](https://marqius.com/wkhtmltopdf/download/) does, run `marqius-wkhtmltopdf install` with the rights to write to `/usr/local/bin`.

## Always the latest release

Each release of this package carries one release of marqius-wkhtmltopdf, with the same version number. [A workflow](https://github.com/marqiushq/marqius-wkhtmltopdf-python/blob/main/.github/workflows/release.yml) follows marqius.com every hour: a new release is checked against its published checksums, installed with pip and run through python-pdfkit, django-wkhtmltopdf and imgkit on Linux (x86-64 and ARM64), macOS (Apple silicon) and Windows, and only then published. To move to it:

```bash
pip install --upgrade marqius-wkhtmltopdf
```

## Licence

marqius-wkhtmltopdf is commercial software from Simple AI LLC, with a 30-day free trial counted from its first run. After the trial, without a licence, each page carries one line saying the copy is unlicensed. [Plans and licences](https://marqius.com/licence/marqius-wkhtmltopdf) · [Licence terms](https://marqius.com/wkhtmltopdf/licence-agreement/)

## Before you switch

- [wkhtmltopdf parity suite](https://github.com/marqiushq/wkhtmltopdf-parity): the same HTML documents through wkhtmltopdf and marqius-wkhtmltopdf on every release, misses included.
- [The developer manual](https://marqius.com/download/developer-manual.pdf), one chapter per library, and [runnable examples](https://github.com/marqiushq/marqius-wkhtmltopdf-examples).
