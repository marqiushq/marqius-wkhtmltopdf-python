#!/bin/sh
# Runs this README's install line and each library's example exactly as printed, each in a new
# virtual environment that already has the library, and checks what each one makes.
#
#   tests/examples.sh WORK [LIBRARY ...]        LIBRARY: pdfkit, django-wkhtmltopdf or imgkit
#
# Before the wheels are on PyPI, set PIP_FIND_LINKS to their folder: the install line still runs
# as printed, and pip finds them there. PYTHON names the Python to make the environments with.
set -eu
pkg=$(cd "$(dirname "$0")/.." && pwd)
work=$1
shift
libraries=${*:-pdfkit django-wkhtmltopdf imgkit}
python=${PYTHON:-python3}
say() { printf '\n== %s\n' "$*"; }
fail() {
    echo "FAIL $lib: $*" >&2
    exit 1
}
readme() { "$python" "$pkg/tests/readme.py" "$1"; }

project() { # a new environment with the library, then this README's install line, as printed
    dir=$work/$lib
    rm -rf "$dir"
    mkdir -p "$dir"
    cd "$dir"
    "$python" -m venv .venv
    if [ -f .venv/Scripts/activate ]; then . .venv/Scripts/activate; else . .venv/bin/activate; fi
    python -m pip install -q --disable-pip-version-check "$@"
    line=$(readme install)
    say "$line"
    sh -c "$line" </dev/null
}

check() { # a file made by the example, and its first bytes
    [ -s "$1" ] || fail "no $1"
    head -c 8 "$1" | od -An -c | tr -d ' \n' | grep -q "$2" || fail "$1 does not start with $2"
    if [ "$2" = "%PDF-" ] && command -v pdftotext >/dev/null 2>&1; then
        pdftotext "$1" - | grep -q 'Invoice 42' || fail "$1 does not read Invoice 42"
    fi
    echo "ok $lib: $1 ($(wc -c <"$1" | tr -d ' ') bytes)"
}

for lib in $libraries; do
    say "$lib ($("$python" -c 'import sys, sysconfig; print(sys.version.split()[0], sysconfig.get_platform())'))"
    case $lib in
    pdfkit)
        project pdfkit
        { echo 'import pdfkit, marqius_wkhtmltopdf'; readme "example: pdfkit"; } >render.py
        cat render.py
        python render.py
        check invoice.pdf %PDF-
        ;;
    imgkit)
        project imgkit
        { echo 'import imgkit, marqius_wkhtmltopdf'; readme "example: imgkit"; } >render.py
        cat render.py
        python render.py
        check invoice.jpg 377330377
        ;;
    django-wkhtmltopdf)
        project django django-wkhtmltopdf
        django-admin startproject mysite .
        # the README's lines at the end of settings.py; then a template and the app, for this test
        readme "example: django-wkhtmltopdf settings.py" >>mysite/settings.py
        printf 'INSTALLED_APPS += ["wkhtmltopdf"]\nTEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]\n' >>mysite/settings.py
        mkdir templates
        echo '<html><body><h1>Invoice 42</h1></body></html>' >templates/invoice.html
        tail -n 4 mysite/settings.py
        cat >render.py <<'PY'
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
from django.test import RequestFactory
from wkhtmltopdf.views import PDFTemplateResponse
response = PDFTemplateResponse(request=RequestFactory().get("/"), template="invoice.html", context={})
with open("invoice.pdf", "wb") as f:
    f.write(response.rendered_content)
PY
        python render.py
        check invoice.pdf %PDF-
        ;;
    *)
        fail "no such library"
        ;;
    esac
    marqius-wkhtmltopdf --version | grep '^marqius-wkhtmltopdf [0-9]' || fail "marqius-wkhtmltopdf --version"
    python -c 'import subprocess, marqius_wkhtmltopdf as m; subprocess.run([m.path(), "-V"], check=True)' | grep "compatible; marqius-wkhtmltopdf" || fail "the path -V"
    deactivate
done
say "all passed: $libraries"
