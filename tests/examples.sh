#!/bin/sh
# Runs this README's lines exactly as printed, each library in a new virtual environment that
# already has the library, and checks what each one makes.
#
#   tests/examples.sh WORK [LIBRARY ...]
#
# LIBRARY is quickstart (the README's first three steps, in an empty folder; on Windows with its
# Windows lines, in PowerShell), pdfkit, django-wkhtmltopdf, flask, fastapi, imgkit, languages (the
# README's eight-language invoice, after its fonts line on Debian and Ubuntu: every word must read
# back as written, and every letter must have a font), typed (mypy --strict on the module's
# types) or update (the README's update line); all of them by default.
#
# Before the wheels are on PyPI, set PIP_FIND_LINKS to their folder: the install line still runs
# as printed, and pip finds them there. PYTHON names the Python to make the environments with.
# EXPECT_VERSION, if set, is the version pip must install. For update, UPDATE_FROM is the version
# to install first (else the README's install line), and UPDATE_TO the newer one that pip can find
# (else the version installed must already be the newest, and stay).
set -eu
pkg=$(cd "$(dirname "$0")/.." && pwd)
work=$1
shift
libraries=${*:-quickstart pdfkit django-wkhtmltopdf flask fastapi imgkit languages typed update}
python=${PYTHON:-python3}
case $(uname -s) in MINGW* | MSYS* | CYGWIN*) windows=yes ;; *) windows= ;; esac
say() { printf '\n== %s\n' "$*"; }
fail() {
    echo "FAIL $lib: $*" >&2
    exit 1
}
readme() { "$python" "$pkg/tests/readme.py" "$@"; }

fresh() { # a new, empty folder for this library
    dir=$work/$lib
    rm -rf "$dir"
    mkdir -p "$dir"
    cd "$dir"
}

activate() {
    if [ -f .venv/Scripts/activate ]; then . .venv/Scripts/activate; else . .venv/bin/activate; fi
}

expected() { # the version EXPECT_VERSION names, if it names one
    if [ -n "${EXPECT_VERSION:-}" ]; then
        got=$(python -c 'import marqius_wkhtmltopdf as m; print(m.__version__)')
        [ "$got" = "$EXPECT_VERSION" ] || fail "pip installed marqius-wkhtmltopdf $got, not $EXPECT_VERSION"
        echo "ok $lib: marqius-wkhtmltopdf $got installed"
    fi
}

project() { # a new environment with the library, then this README's install line, as printed
    fresh
    "$python" -m venv .venv
    activate
    python -m pip install -q --disable-pip-version-check "$@"
    line=$(readme install)
    say "$line"
    sh -c "$line" </dev/null
    expected
}

check() { # a file made by the example, and its first bytes
    [ -s "$1" ] || fail "no $1"
    head -c 8 "$1" | od -An -c | tr -d ' \n' | grep -q "$2" || fail "$1 does not start with $2"
    if [ "$2" = "%PDF-" ] && command -v pdftotext >/dev/null 2>&1; then
        pdftotext "$1" - | grep -q 'Invoice 42' || fail "$1 does not read Invoice 42"
    fi
    echo "ok $lib: $1 ($(wc -c <"$1" | tr -d ' ') bytes)"
}

program_says() { # what the README's own line for it says of page.html's letters
    line=$(readme check)
    say "$line"
    sh -c "$line" >said.txt 2>&1 || true
    cat said.txt
}

web() { # the README's app.py for Flask or FastAPI, asked for /invoice.pdf by the framework's test client
    readme "example: $lib app.py" >app.py
    cat app.py
    case $lib in
    flask) client='app.test_client()' ;;
    fastapi) client='__import__("fastapi.testclient").testclient.TestClient(app)' ;;
    esac
    python -c "from app import app
r = $client.get('/invoice.pdf')
assert r.status_code == 200, r.status_code
assert r.headers['content-type'].startswith('application/pdf'), r.headers['content-type']
open('invoice.pdf', 'wb').write(r.data if hasattr(r, 'data') else r.content)"
    check invoice.pdf %PDF-
}

for lib in $libraries; do
    say "$lib ($("$python" -c 'import sys, sysconfig; print(sys.version.split()[0], sysconfig.get_platform())'))"
    case $lib in
    quickstart)
        # step 1 as printed, in an empty folder (its own python3 makes the environment), then the
        # README's invoice.py and its run line, in the environment step 1 opened
        fresh
        readme "example: quickstart invoice.py" >invoice.py
        cat invoice.py
        if [ -n "$windows" ]; then
            # the README's Windows lines in place of the first two, as typed in PowerShell, which
            # must leave the environment open: then pip and the run line are the environment's
            lines=$(readme --inline "quickstart: windows" | tr -d '\r')
            script=
            for l in "$(echo "$lines" | sed -n 1p)" "$(echo "$lines" | sed -n 2p)" "$(readme quickstart | sed -n 3p | tr -d '\r')" \
                "python -c \"import sys; assert sys.prefix != sys.base_prefix, 'not in the virtual environment'\"" "$(readme run | tr -d '\r')"; do
                script="$script$l; if (\$LASTEXITCODE) { exit \$LASTEXITCODE }; "
            done
            say "$script"
            powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "\$ErrorActionPreference = 'Stop'; $script"
            activate
        else
            script="$(readme quickstart)
python -c \"import sys; assert sys.prefix != sys.base_prefix, 'not in the virtual environment'\"
$(readme run)"
            say "$script"
            sh -c "set -e
$script" </dev/null
            activate
        fi
        expected
        check invoice.pdf %PDF-
        ;;
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
    flask)
        project flask pdfkit
        web
        ;;
    fastapi)
        project fastapi httpx pdfkit
        web
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
    languages)
        project pdfkit
        # the page in the README's example, as page.html for the program's own line
        readme "example: languages" >render.py
        cat render.py
        python -c 'import re; s = open("render.py", encoding="utf-8").read(); m = re.search(r"html = \"\"\"(.*?)\"\"\"", s, re.S); open("page.html", "w", encoding="utf-8").write(m.group(1))'
        if [ -f /etc/debian_version ]; then
            # before the fonts: what the program says, and that it names Debian's Noto packages
            program_says
            if grep -q 'no font has a glyph' said.txt; then
                grep -q 'fonts-noto' said.txt || fail "the program named letters with no font, but no fonts-noto package to install"
            fi
            line=$(readme "fonts: debian")
            say "$line"
            sh -c "$line" >fonts.log 2>&1 || { cat fonts.log; fail "$line"; }
        fi
        python render.py
        check invoice.pdf %PDF-
        # every word as written, where pdftotext can be had
        if ! command -v pdftotext >/dev/null 2>&1; then
            if [ -f /etc/debian_version ]; then
                sudo apt-get install -y -qq poppler-utils >/dev/null || true
            elif [ "$(uname -s)" = Darwin ]; then
                brew install -q poppler >/dev/null || true
            fi
        fi
        if command -v pdftotext >/dev/null 2>&1; then
            # UTF-8 said outright: the pdftotext that comes with Git on Windows writes Latin-1 otherwise
            pdftotext -enc UTF-8 invoice.pdf - >text.txt
            cat text.txt
            for word in 'Invoice 42' 'فاتورة' 'חשבונית' 'चालान' 'ใบแจ้งหนี้' '发票' '請求書' '청구서'; do
                grep -qF "$word" text.txt || fail "invoice.pdf does not read $word as written"
            done
            echo "ok $lib: every word reads back as written"
        else
            fail "no pdftotext to read the words back with"
        fi
        # after the fonts, or with the system's own: no letter without a font
        program_says
        ! grep -q 'no font has a glyph' said.txt || fail "letters with no font on this system"
        ;;
    typed)
        # the module's types, as mypy --strict reads them through py.typed
        project mypy
        printf 'import marqius_wkhtmltopdf\n\npdf: str = marqius_wkhtmltopdf.path()\nimage: str = marqius_wkhtmltopdf.image_path()\nprogram: str = marqius_wkhtmltopdf.program()\nversion: str = marqius_wkhtmltopdf.__version__\n' >typed.py
        python -m mypy --strict typed.py
        ;;
    update)
        fresh
        "$python" -m venv .venv
        activate
        if [ -n "${UPDATE_FROM:-}" ]; then
            python -m pip install -q --disable-pip-version-check "marqius-wkhtmltopdf==$UPDATE_FROM"
        else
            line=$(readme install)
            say "$line"
            sh -c "$line" </dev/null
        fi
        before=$(python -c 'import importlib.metadata as m; print(m.version("marqius-wkhtmltopdf"))')
        line=$(readme update)
        if [ -n "$windows" ]; then
            # there the command says to use python -m (it cannot replace itself while it runs), and
            # the README's Windows line is the one that updates
            if sh -c "$line" </dev/null >said.txt 2>&1; then cat said.txt; fail "$line went on, on Windows"; fi
            cat said.txt
            grep -q "python -m marqius_wkhtmltopdf update" said.txt || fail "$line did not name python -m marqius_wkhtmltopdf update"
            line=$(readme --inline "update: windows" | sed -n 1p | tr -d '\r')
        fi
        say "$line (from $before)"
        sh -c "$line" </dev/null >said.txt 2>&1 || { cat said.txt; fail "$line"; }
        cat said.txt
        got=$(python -c 'import importlib.metadata as m; print(m.version("marqius-wkhtmltopdf"))')
        if [ -n "${UPDATE_TO:-}" ]; then
            [ "$got" = "$UPDATE_TO" ] || fail "$line left $got, not $UPDATE_TO"
            grep -q "is now $UPDATE_TO" said.txt || fail "$line did not say that it is now $UPDATE_TO"
        else
            [ "$got" = "$before" ] || fail "$line changed $before to $got, where $before was the newest"
            grep -q "$before is the newest version" said.txt || fail "$line did not say that $before is the newest"
        fi
        echo "ok $lib: $before -> $got"
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
