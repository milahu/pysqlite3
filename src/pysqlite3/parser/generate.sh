#!/bin/sh
set -e
ksc=$KSC # use ksc from env
[ -z "$ksc" ] && ksc=$(which kaitai-struct-compiler 2>/dev/null)
set -x
cd "$(dirname "$0")"
$ksc -t python --python-package . sqlite3.ksy
black .
