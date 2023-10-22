#! /usr/bin/env python3

import sys
import os

sys.path.append(os.path.dirname(__file__) + "/../src")
import pysqlite3

os.chdir(os.path.dirname(__file__))
database = "example-partial.db"

con = pysqlite3.connect(database, allow_bad_size=True)

print(f"page size: {con._db.header.page_size} bytes")
print(f"db size: {con._db.header.num_pages} pages")
print(f"idx_lock_byte_page: {con._db.header.idx_lock_byte_page}")
print(f"idx_first_ptrmap_page: {con._db.header.idx_first_ptrmap_page}")
print(f"idx_last_ptrmap_page: {con._db.header.idx_last_ptrmap_page}")
print(f"con._db.pages =", con._db.pages)
print("tables =", con._tables)

print("con._columns")
for table in con._tables:
    try:
        print(f"table {table}: columns =", con._columns(table))
    except NotImplementedError as err:
        print("ignoring NotImplementedError:", err)

def format_values(values):
    result = []
    max_len = 50
    for val in values:
        s = repr(val)
        if len(s) > max_len:
            s = s[0:max_len] + "..."
        result.append(s)
    return "[" + ", ".join(result) + "]"

print("con._table_values")
for table in con._tables:
    print(f"con._table_values(table={repr(table)})")
    num_rows = 0
    for row_id, values in enumerate(con._table_values(table)):
        num_rows += 1
        print(f"table {table}: row {row_id + 1} =", format_values(values))
