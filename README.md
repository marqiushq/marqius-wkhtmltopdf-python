# wkhtmltopdf for Python: marqius-wkhtmltopdf for pdfkit, Django, Flask and imgkit

[![PyPI](https://img.shields.io/pypi/v/marqius-wkhtmltopdf)](https://pypi.org/project/marqius-wkhtmltopdf/) [![Python](https://img.shields.io/pypi/pyversions/marqius-wkhtmltopdf)](https://pypi.org/project/marqius-wkhtmltopdf/)

**marqius-wkhtmltopdf is the maintained drop-in replacement for wkhtmltopdf, installed with pip.** Install it with one command, give your library its path in one line, and python-pdfkit, django-wkhtmltopdf and imgkit turn your HTML into PDFs and pictures as before. It prints Arabic, Hebrew, Hindi, Thai, Chinese, Japanese and Korean as well as English, on Linux, Mac and Windows.

- **One command to install.** No apt packages, no libssl 1.1, no X server, no Qt: the wheel carries the program.
- **Your templates stay as they are.** The same HTML, the same options, the same library.
- **Many languages, even on one page.** Arabic and Hebrew from right to left, Indian and Asian scripts, all as text you can search and copy.
- **Fast.** A one-page invoice takes a few milliseconds.
- **Tested in public.** Every version is tested with python-pdfkit, django-wkhtmltopdf, Flask, FastAPI and imgkit on Linux, macOS and Windows before it is published.

## Make your first PDF in two minutes

**1. Install** the package and pdfkit, the most used Python library for wkhtmltopdf. In an empty folder, make a virtual environment and install them:

<!-- quickstart -->
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install marqius-wkhtmltopdf pdfkit
```

<!-- quickstart: windows -->
On Windows, the first two lines are `python -m venv .venv` and `.venv\Scripts\activate`.

**2. Save** this as `invoice.py`:

<!-- example: quickstart invoice.py -->
```python
import marqius_wkhtmltopdf
import pdfkit

config = pdfkit.configuration(wkhtmltopdf=marqius_wkhtmltopdf.path())
pdfkit.from_string("<h1>Invoice 42</h1><p>Thank you for your order.</p>", "invoice.pdf", configuration=config)
```

**3. Run** it, then open `invoice.pdf`:

<!-- run -->
```bash
python invoice.py
```

That's it. Next, connect your framework, or [print other languages](#which-languages-can-it-print).

## What do I change in my code?

| You use | What to do |
|---|---|
| python-pdfkit, in any Python code | [Give it `marqius_wkhtmltopdf.path()`](#how-do-i-use-wkhtmltopdf-with-python-pdfkit) |
| Django, with django-wkhtmltopdf | [Two lines in `settings.py`](#how-do-i-use-wkhtmltopdf-in-django) |
| Flask or FastAPI | [pdfkit, in your route](#how-do-i-send-a-pdf-from-flask-or-fastapi) |
| imgkit, for pictures | [Give it `marqius_wkhtmltopdf.image_path()`](#how-do-i-make-pictures-with-imgkit) |

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

## How do I use wkhtmltopdf in Django?

With django-wkhtmltopdf, name it in your project's `settings.py`:

<!-- example: django-wkhtmltopdf settings.py -->
```python
import marqius_wkhtmltopdf, shlex
WKHTMLTOPDF_CMD = shlex.quote(marqius_wkhtmltopdf.path())
```

django-wkhtmltopdf reads `WKHTMLTOPDF_CMD` as a command line, so the path is quoted. Your `PDFTemplateView` and `PDFTemplateResponse` views then make PDFs as before.

## How do I send a PDF from Flask or FastAPI?

Make it with pdfkit and send the bytes: `False` in place of a file name gives you the PDF itself. In Flask:

<!-- example: flask app.py -->
```python
import marqius_wkhtmltopdf, pdfkit
from flask import Flask, Response

app = Flask(__name__)
config = pdfkit.configuration(wkhtmltopdf=marqius_wkhtmltopdf.path())

@app.route("/invoice.pdf")
def invoice():
    pdf = pdfkit.from_string("<h1>Invoice 42</h1>", False, configuration=config)
    return Response(pdf, mimetype="application/pdf")
```

In FastAPI:

<!-- example: fastapi app.py -->
```python
import marqius_wkhtmltopdf, pdfkit
from fastapi import FastAPI, Response

app = FastAPI()
config = pdfkit.configuration(wkhtmltopdf=marqius_wkhtmltopdf.path())

@app.get("/invoice.pdf")
def invoice():
    pdf = pdfkit.from_string("<h1>Invoice 42</h1>", False, configuration=config)
    return Response(pdf, media_type="application/pdf")
```

## How do I make pictures with imgkit?

Give imgkit the path for pictures, `marqius_wkhtmltopdf.image_path()`. Where your code has `import imgkit, marqius_wkhtmltopdf`:

<!-- example: imgkit -->
```python
config = imgkit.config(wkhtmltoimage=marqius_wkhtmltopdf.image_path())
imgkit.from_string("<h1>Invoice 42</h1>", "invoice.jpg", config=config)
```

## Which languages can it print?

All of these, even on one page. Each one is tested on real invoices, letters and receipts, and the PDF keeps the words as text, so you can search and copy them.

| Language | On a Linux server | On a Mac or Windows |
|---|---|---|
| English, French, German, Spanish and other languages in Latin letters; Greek; Russian | Works with the fonts most servers have | Works |
| Arabic and Hebrew, from right to left | Works: the fonts are built in | Works |
| Hindi and Thai | Install `fonts-noto-core` | Works |
| Chinese, Japanese and Korean | Install `fonts-noto-cjk` | Works |

On Debian or Ubuntu, this one line installs the fonts for every language above:

<!-- fonts: debian -->
```bash
sudo apt-get update && sudo apt-get install -y fonts-noto-core fonts-noto-cjk
```

In a Dockerfile, put the same line after `RUN`, without `sudo`. On Alpine, Fedora, Red Hat or Arch, the program tells you the line for your system ([see below](#why-do-letters-show-as-boxes-or-blanks-in-my-pdf)).

Then one invoice can carry them all, here with pdfkit:

<!-- example: languages -->
```python
import marqius_wkhtmltopdf, pdfkit

html = """<!doctype html>
<meta charset="utf-8">
<h1>Invoice 42</h1>
<p lang="ar" dir="rtl">فاتورة 42</p>
<p lang="he" dir="rtl">חשבונית 42</p>
<p lang="hi">चालान 42</p>
<p lang="th">ใบแจ้งหนี้ 42</p>
<p lang="zh">发票 42</p>
<p lang="ja">請求書 42</p>
<p lang="ko">청구서 42</p>
"""

config = pdfkit.configuration(wkhtmltopdf=marqius_wkhtmltopdf.path())
pdfkit.from_string(html, "invoice.pdf", configuration=config)
```

For a page all in Arabic or Hebrew, put `dir="rtl"` on its `<html>` tag. The page then reads from the right, and its tables and lists turn to match.

## Why do letters show as boxes or blanks in my PDF?

The computer that makes the PDF has no font for them. On Linux, install the fonts [above](#which-languages-can-it-print). To see what is missing, convert your page with the program itself, in your virtual environment:

<!-- check -->
```bash
marqius-wkhtmltopdf page.html page.pdf
```

It names each letter it could not print, then gives the one line that installs fonts for them on your system: `apt-get` on Debian and Ubuntu, `apk` on Alpine, `dnf` on Fedora and Red Hat, `pacman` on Arch.

## Why can't I search or copy Arabic, Chinese or Hindi text in my wkhtmltopdf PDF?

wkhtmltopdf often stores these scripts as shapes, not words. The public parity suite prints the same pages with both programs:

- **Arabic:** from wkhtmltopdf's invoice, 2 of its 56 words read back as written; from marqius-wkhtmltopdf's, 48.
- **Hebrew:** wkhtmltopdf splits many words into single letters (28 of 48 read back); marqius-wkhtmltopdf gives back 43.
- **Chinese:** wkhtmltopdf puts look-alike signs in place of some characters, so a search for the company's name finds nothing. marqius-wkhtmltopdf keeps the real characters.
- **Hindi and Thai:** wkhtmltopdf loses letters and splits off marks. marqius-wkhtmltopdf's text reads back clean.

The pages themselves look the same. [See every page and score](https://github.com/marqiushq/wkhtmltopdf-parity).

## Why are accented letters garbled, like Ã© for é?

Your page does not say that it is UTF-8, so wkhtmltopdf reads it as an old Western character set. marqius-wkhtmltopdf prints é, € and ü as written anyway. To make every program agree, put `<meta charset="utf-8">` at the top of your page.

## Why do I get "No wkhtmltopdf executable found"?

python-pdfkit says this when it cannot find a wkhtmltopdf program. Install this package and give pdfkit `marqius_wkhtmltopdf.path()`, as shown above.

## Why does wkhtmltopdf fail with "libssl.so.1.1: cannot open shared object file"?

Your wkhtmltopdf was built for an older system. It needs OpenSSL 1.1, which Debian 13 and Ubuntu 24.04 no longer include. marqius-wkhtmltopdf needs no system libraries, so it runs there as it is.

## Is it faster than wkhtmltopdf?

Yes. The public parity suite converts 86 documents with both programs on the same machine. marqius-wkhtmltopdf is 35 times faster, or 5 times faster with wkhtmltopdf's 200 ms wait for scripts turned off for both. On Linux, a one-page invoice takes 5 to 7 milliseconds. [See the results](https://github.com/marqiushq/wkhtmltopdf-parity).

## Will my PDFs look the same as with wkhtmltopdf?

Almost always. Of the parity suite's 86 documents, 64 come out the same, and 16 differ only in small details of appearance. Each difference is listed with its reason. To check your own templates, make a PDF with each program and compare them:

```bash
marqius-wkhtmltopdf compare old.pdf new.pdf
```

## Which systems does it run on?

It runs on:

- Linux on x86-64 and ARM64, with glibc or musl, so Debian 13, Ubuntu 24.04 and Alpine too;
- Macs with Apple silicon;
- Windows on x86-64.

It works with Python 3.8 to 3.14. pip installs the right wheel for each system, a download of about 10 MB. It needs no X server, Qt or system libraries. In a slim or Alpine image without fonts, the program says so and prints the one line that installs them.

## Why does pip say "Could not find a version that satisfies the requirement marqius-wkhtmltopdf"?

pip found no wheel for your computer. There is none for Macs with Intel chips, for 32-bit Python, or for Python older than 3.8. Use one of the systems above, with a 64-bit Python 3.8 or newer.

## Is marqius-wkhtmltopdf free?

You can try it free for 30 days. Personal, teaching and open-source use is free with a [Community licence](https://marqius.com/wkhtmltopdf-buy/#community): sign in with Google and your free key is waiting in your account.

Anything done by or for a business, including internal tools and client work, needs a paid plan once the trial ends. [See the plans and prices](https://marqius.com/licence/marqius-wkhtmltopdf).

Your PDFs never stop. Without a licence after the trial, each page carries one line, "Prepared by Marqius, Purchase Licence". [Licence terms](https://marqius.com/wkhtmltopdf/licence-agreement/)

## How do I add my licence key?

Set the `MARQIUS_LICENCE` environment variable to your licence; that is the way for containers and CI. Or save it as `licence.txt` and run `marqius-wkhtmltopdf licence add licence.txt`. `marqius-wkhtmltopdf licence` shows the trial's days left, or the licence in force.

## Do these libraries pass their own tests?

python-pdfkit and imgkit pass their own test suites with marqius-wkhtmltopdf: all 47 of python-pdfkit's tests and all 48 of imgkit's. django-wkhtmltopdf's suite gives the same results as with wkhtmltopdf 0.12.6. The results are public: [wkhtmltopdf library tests](https://github.com/marqiushq/wkhtmltopdf-library-tests).

Before each version of this package is published, [its workflow](https://github.com/marqiushq/marqius-wkhtmltopdf-python/blob/main/.github/workflows/release.yml) installs it with pip and runs the examples on this page, the eight-language invoice among them, on Linux (x86-64 and ARM64), macOS and Windows, and with Python 3.8 and 3.14 on Linux.

## How do I update it?

Run this in your virtual environment. It installs the newest version with pip, or with uv if uv installed it:

<!-- update -->
```bash
marqius-wkhtmltopdf update
```

<!-- update: windows -->
On Windows, run `python -m marqius_wkhtmltopdf update` instead: Windows does not let a running command replace itself.

`pip install --upgrade marqius-wkhtmltopdf` does the same. This package follows each release of marqius-wkhtmltopdf, after testing it. A version with a fourth number, such as 0.12.13.1, changes only this package: it carries the program of 0.12.13.

## What else does the program do?

The package also installs the command `marqius-wkhtmltopdf`:

- `marqius-wkhtmltopdf help python-pdfkit` shows each library's setting;
- `marqius-wkhtmltopdf compare old.pdf new.pdf` lists every difference between a PDF made by wkhtmltopdf and one made by marqius-wkhtmltopdf;
- `marqius-wkhtmltopdf install` gives it the names `wkhtmltopdf` and `wkhtmltoimage` for everything on a server, with the rights to write to `/usr/local/bin`.

## Where do I get help?

Write to hello@marqius.com, or [open an issue](https://github.com/marqiushq/marqius-wkhtmltopdf-python/issues). Send the page that prints differently from wkhtmltopdf if you can.

This package's own Python files are under the MIT licence: [LICENSE.md](https://github.com/marqiushq/marqius-wkhtmltopdf-python/blob/main/LICENSE.md).
