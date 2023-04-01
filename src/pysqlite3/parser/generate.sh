#!/bin/sh
ksc=$KSC # use ksc from env
[ -z "$ksc" ] && ksc=$(which kaitai-struct-compiler 2>/dev/null)
set -x
cd "$(dirname "$0")"
exec $ksc -t python --python-package . sqlite3.ksy
