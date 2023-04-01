#!/bin/sh

set -e

ksc=$KSC # use ksc from env
[ -z "$ksc" ] && ksc=$(which kaitai-struct-compiler 2>/dev/null)

set -x

cd "$(dirname "$0")"

# generate sqlite3.py and vlq_base128_be.py
$ksc -t python --python-package . sqlite3.ksy

# reformat python files
black .

# use local kaitaistruct.py
sed -i '
    s/^import kaitaistruct$/from . import kaitaistruct/;
    s/^from kaitaistruct import/from .kaitaistruct import/;
' *.py
