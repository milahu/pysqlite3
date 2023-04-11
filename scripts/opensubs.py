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


def compress_value_positions(value_positions):
    """
    compress value positions
    compress neighbor pages to ranges
    example: 1,2,3,4,5 = 1-5
    only the first chunk has variable size
    all following chunks have the maximum chunk size = (usable_size - 4)
    con._db.header.usable_size - 4
    first position is usually (always?) separate from the following positons
    following positons are usually (always?) packed together
    example:
    [(14, 422, 3666), (2, 0, 4092), (3, 0, 4092), (4, 0, 4092), (5, 0, 4092), (6, 0, 4092), (7, 0, 4092), (8, 0, 4092)]
    compress this to:
    14,422,3666+2-8
    this means:
    - at page 14: seek to 422 and read 3666 bytes
    - at pages 2 to 8: seek to 0 and read 4092 bytes
    4092 is a global constant: 4092 = con._db.header.usable_size - 4
    """
    first_page_idx = value_positions[0][0]
    result = ",".join(map(str, value_positions[0])) # first page
    # following pages
    if len(value_positions) > 1:
        second_page_idx = value_positions[1][0]
        result += f"+{second_page_idx}"
    if len(value_positions) > 2:
        # assert that all following pages are packed
        # probably, this is not always the case
        # and we need multiple ranges
        for idx, pos in enumerate(value_positions):
            if idx < 2: continue
            last_pos = value_positions[idx - 1]
            # assert that page index is steady (always +1)
            assert last_pos[0] + 1 == pos[0], f"last page {idx-1}:{last_pos[0]}, page {idx}:{pos[0]}"
        # we can further compress this if last_page == (first_page - 1)
        last_page_idx = value_positions[-1][0]
        if last_page_idx == (first_page_idx - 1):
            result += f"-" # compressed last_page_idx
        else:
            result += f"-{last_page_idx}"
        # TODO we can further compress this
        # by printing second_page_idx and last_page_idx relative to first_page_idx
    return result


def compress_zip_name(zip_name, num):
    """
    TODO further compress the name:
    - .zip is not needed
    - the subtitle_id (804) is redundant with the num column
    - 2cd is too verbose, its always either "1cd" or "2cd",
    so we only need the parts_count: 1 or 2
    - remove parens from year
    see also ../opensubtitles_dump_client/index.py
    TODO assert parsed_num == num
    """
    return zip_name


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

    for values in con._table_values("subz"):

        num, name, file_ = values

        # extract filename
        # a: attachment; filename="xxx"
        # b: xxx
        name = compress_zip_name(name[22:-1], num)

        value_positions = compress_value_positions(con._last_value_positions)

        print(num, name, value_positions)

main()
