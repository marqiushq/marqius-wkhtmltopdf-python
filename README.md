# marqius-wkhtmltopdf: wkhtmltopdf for Python, pdfkit, django-wkhtmltopdf and imgkit

**marqius-wkhtmltopdf is the maintained drop-in replacement for wkhtmltopdf, as a Python package.** `pip install` it, give your library its path in one line, and python-pdfkit, django-wkhtmltopdf or imgkit keep making PDFs and pictures from your HTML. It runs on Linux (x86-64 and ARM64, glibc and musl, including Debian 13, Ubuntu 24.04 and Alpine), Apple silicon Macs and Windows (x86-64).

## How do I install wkhtmltopdf with pip?

<!-- install -->
```bash
pip install marqius-wkhtmltopdf
```

pip installs the wheel for your platform, which carries the program itself, so nothing else is downloaded, at install or when your code runs. It installs nothing under the name `wkhtmltopdf` on your system: your library gets the program's path from `marqius_wkhtmltopdf.path()`, as below.

## How do I use wkhtmltopdf with python-pdfkit?

Give pdfkit the path. Where your code has `import pdfkit, marqius_wkhtmltopdf`:

<!-- example: pdfkit -->
```python
config = pdfkit.configuration(wkhtmltopdf=marqius_wkhtmltopdf.path())
pdfkit.from_string("<h1>Invoice 42</h1>", "invoice.pdf", configuration=config)
```

## How do I use it with django-wkhtmltopdf?

Name it in your project's `settings.py`:

<!-- example: django-wkhtmltopdf settings.py -->
```python
import marqius_wkhtmltopdf, shlex
WKHTMLTOPDF_CMD = shlex.quote(marqius_wkhtmltopdf.path())
```

django-wkhtmltopdf reads `WKHTMLTOPDF_CMD` as a command line, so the path is quoted. Your `PDFTemplateView` and `PDFTemplateResponse` views then make PDFs as before.

## How do I make pictures with imgkit?

Give imgkit the path for pictures, `marqius_wkhtmltopdf.image_path()`. Where your code has `import imgkit, marqius_wkhtmltopdf`:

<!-- example: imgkit -->
```python
config = imgkit.config(wkhtmltoimage=marqius_wkhtmltopdf.image_path())
imgkit.from_string("<h1>Invoice 42</h1>", "invoice.jpg", config=config)
```

## Why do I get "No wkhtmltopdf executable found"?

python-pdfkit says this when it cannot find a wkhtmltopdf program. Install this package and give pdfkit `marqius_wkhtmltopdf.path()`, as shown above.

## Why does wkhtmltopdf fail with "libssl.so.1.1: cannot open shared object file"?

Your wkhtmltopdf was built for an older system. It needs OpenSSL 1.1, which Debian 13 and Ubuntu 24.04 no longer include. marqius-wkhtmltopdf needs no system libraries, so it runs there as it is.

## Which systems does marqius-wkhtmltopdf run on?

It runs on:

- Linux on x86-64 and ARM64, with glibc or musl (so Alpine too);
- Macs with Apple silicon;
- Windows on x86-64.

pip installs the right wheel for each. It needs no X server, Qt or system libraries. In a slim or Alpine image without fonts, the program says so and prints the one line that installs them.

## Is marqius-wkhtmltopdf free?

You can try it free for 30 days. Personal, teaching and open-source use is free with a [Community licence](https://marqius.com/wkhtmltopdf-buy/#community): sign in with Google and your free key is waiting in your account.

Anything done by or for a business, including internal tools and client work, needs Starter or above once the trial ends. Starter is $290 USD a year for organisations of up to 10 people, and Business $990 USD a year, plus applicable taxes.

Your PDFs never stop. Without a licence after the trial, each page carries one line, "Prepared by Marqius, Purchase Licence". [Plans and licences](https://marqius.com/licence/marqius-wkhtmltopdf) · [Licence terms](https://marqius.com/wkhtmltopdf/licence-agreement/)

## How do I add my licence key?

Set the `MARQIUS_LICENCE` environment variable to your licence; that is the way for containers and CI. Or save it as `licence.txt` and run `marqius-wkhtmltopdf licence add licence.txt`. `marqius-wkhtmltopdf licence` shows the trial's days left, or the licence in force.

## Do these libraries pass their own tests?

python-pdfkit and imgkit pass their own test suites with marqius-wkhtmltopdf: all 47 of python-pdfkit's tests and all 48 of imgkit's. django-wkhtmltopdf's suite gives the same results as with wkhtmltopdf 0.12.6. The results are public: [wkhtmltopdf library tests](https://github.com/marqiushq/wkhtmltopdf-library-tests).

Before each version of this package is published, [its workflow](https://github.com/marqiushq/marqius-wkhtmltopdf-python/blob/main/.github/workflows/release.yml) installs it with pip and runs the examples on this page on Linux (x86-64 and ARM64), macOS and Windows.

## How do I update it?

Each version of this package carries the marqius-wkhtmltopdf release with the same number. To move to the newest:

```bash
pip install --upgrade marqius-wkhtmltopdf
```

## What else does the program do?

The package also installs the command `marqius-wkhtmltopdf`:

- `marqius-wkhtmltopdf help python-pdfkit` shows each library's setting;
- `marqius-wkhtmltopdf compare old.pdf new.pdf` lists every difference between a PDF made by wkhtmltopdf and one made by marqius-wkhtmltopdf;
- `marqius-wkhtmltopdf install` gives it the names `wkhtmltopdf` and `wkhtmltoimage` for everything on a server, with the rights to write to `/usr/local/bin`.

This package's own Python files are under the MIT licence: [LICENSE.md](LICENSE.md).
