#! /usr/bin/env python3

"""
get positions of zip files in opensubs.db
so we can build an external index
and do a sparse download of the required torrent pieces
to avoid downloading the full 130GB torrent
"""

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

import subprocess
from typing import List, Tuple
import hashlib

import pysqlite3

dbfile = "../opensubs.db"

con = None
parser_sqlite3 = pysqlite3._parser
parser_sqlite3_helpers = pysqlite3._parser_helpers


def exec(args):
    print("args", repr(args))
    output = subprocess.check_output(args, encoding="utf8")
    print("output", repr(output))
    return output


def main():

    global con

    # tempdir=/run/user/$(id -u)/opensubs
    # mkdir -p $tempdir

    con = pysqlite3.connect(dbfile)

    print(f"page size: {con._db.header.page_size} bytes")
    print(f"db size: {con._db.header.num_pages} pages")
    print(f"usable_size: {con._db.header.usable_size} bytes")
    print(f"overflow_min_payload_size: {con._db.header.overflow_min_payload_size} bytes")

    print(f"tables:", con._tables)
    print(f"schema of subz:", con._schema("subz"))
    print(f"columns of subz:", con._columns("subz"))
    #print(f"column types of subz:", con._column_types("subz"))
    print(f"table values:")
    for values_idx, values in enumerate(con._table_values("subz")):
        num, name, file_ = values
        print(f"values {values_idx}:", (num, name, repr(file_[0:100]) + "..."))

main()
