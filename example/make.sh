#! /usr/bin/env bash

cd "$(dirname "$0")"

rm example.db

sqlite3 example.db '
  create table t1 (a INT);
  create table t2 (a INT);
  insert into t1 values (1);
  insert into t2 values (2);
' 

du -b example.db
# 12288   example.db

sqlite3 example.db 'pragma page_size'
# 4096

expr 12288 / 4096
# 3

# remove page 3
dd if=example.db of=example-partial.db bs=4096 count=2

sqlite3 example-partial.db 'select * from t1'
# Error: in prepare, database disk image is malformed (11)
