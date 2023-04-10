#!/bin/sh

set -e

ksc=$KSC # use ksc from env
[ -z "$ksc" ] && ksc=$(which kaitai-struct-compiler 2>/dev/null)

set -x

cd "$(dirname "$0")"

cp ../../../kaitai_struct_formats/database/sqlite3.ksy sqlite3.ksy || true

# generate sqlite3.py and vlq_base128_be.py
# verbose values: file, value, parent, type_resolve, type_valid, seq_sizes, import, enum_resolve
#$ksc --verbose value -t python --python-package . sqlite3.ksy
$ksc -t python --python-package . sqlite3.ksy

# reformat python files
black .
