#! /usr/bin/env python3

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

import subprocess
from typing import List, Tuple
import hashlib

import pysqlite3

dbfile = "/home/user/src/opensubtitles-dump/opensubs.db"

sqlite3_exe = "/nix/store/fzhf38aczvx61xjlvkk5fwv6dglh713y-sqlite-3.40.1-bin/bin/sqlite3"

con = None
parser_sqlite3 = pysqlite3._parser
parser_sqlite3_helpers = pysqlite3._parser_helpers


def exec(args):
    print("args", repr(args))
    output = subprocess.check_output(args, encoding="utf8")
    print("output", repr(output))
    return output


def get_values(num):

    _debug = False

    data = exec([
        sqlite3_exe,
        dbfile,
        f"select num, sqlite_offset(file), length(file), name from subz where num = {num};"
    ])
    if data == "":
        if _debug:
            print(f"num={num}: no data")
        return None
    num, record_offset, file_length, name = data.split("|", 4)

    num = int(num)
    record_offset = int(record_offset)
    file_length = int(file_length)
    name = name[22:-2]
    page_idx = record_offset // con._db.header.page_size
    page_num = page_idx + 1
    page_offset = page_idx * con._db.header.page_size
    print(f"data:", dict(
        num=num,
        record_offset=record_offset,
        page_idx=page_idx,
        page_offset=page_offset,
        file_length=file_length,
        name=name,
    ))

    _pos = con._db._io.pos()
    db = con._db
    #print("pysqlite3._parser", pysqlite3._parser, dir(pysqlite3._parser))
    #print("pysqlite3._parser.Sqlite3", pysqlite3._parser.Sqlite3, dir(pysqlite3._parser.Sqlite3))
    page = pysqlite3._parser.Sqlite3.Page(page_num, page_offset, db._io, db, db._root)
    con._db._io.seek(_pos)

    cell_pointer_idx = 0

    if _debug:
        #print("page", page, dir(page))
        #print("page.body", page.body, dir(page.body))
        print(f"page.body.ofs_cell_content_area", page.body.ofs_cell_content_area)
        #print("page.body.cell_pointers", page.body.cell_pointers, dir(page.body.cell_pointers))
        # cell[0] is CellPointer
        #print(f"page.body.cell_pointers[{cell_pointer_idx}]", page.body.cell_pointers[cell_pointer_idx], dir(page.body.cell_pointers[cell_pointer_idx]))
        print(f"page.body.cell_pointers[{cell_pointer_idx}].ofs_content", page.body.cell_pointers[cell_pointer_idx].ofs_content)
    ofs_content = page.body.cell_pointers[cell_pointer_idx].ofs_content
    if _debug:
        # content is TableLeafCell
        #print(f"page.body.cell_pointers[{cell_pointer_idx}].content", page.body.cell_pointers[cell_pointer_idx].content, dir(page.body.cell_pointers[cell_pointer_idx].content))
        #print("page.body.cell_pointers[cell_pointer_idx].content.row_id", page.body.cell_pointers[cell_pointer_idx].content.row_id, dir(page.body.cell_pointers[cell_pointer_idx].content.row_id))
        print(f"page.body.cell_pointers[{cell_pointer_idx}].content.row_id.value", page.body.cell_pointers[cell_pointer_idx].content.row_id.value)
    row_id = page.body.cell_pointers[cell_pointer_idx].content.row_id.value
    if _debug:
        # payload is overflow_record because has payload.inline_payload
        print(f"page.body.cell_pointers[{cell_pointer_idx}].content.payload", page.body.cell_pointers[cell_pointer_idx].content.payload, dir(page.body.cell_pointers[cell_pointer_idx].content.payload))
        print(f"page.body.cell_pointers[{cell_pointer_idx}].content.payload_size.value", page.body.cell_pointers[cell_pointer_idx].content.payload_size.value)
        print(f"page.body.cell_pointers[{cell_pointer_idx}].content.payload.payload_size", page.body.cell_pointers[cell_pointer_idx].content.payload.payload_size)
    if hasattr(page.body.cell_pointers[cell_pointer_idx].content.payload, "inline_payload"):
        # payload is overflow_record
        if _debug:
            print(f"page.body.cell_pointers[{cell_pointer_idx}].content.payload.inline_payload_size", page.body.cell_pointers[cell_pointer_idx].content.payload.inline_payload_size)
        # inline_payload: header + body
        # we must parse this manually because paging
        db = con._db
        payload_reader = parser_sqlite3_helpers.PayloadReader(db, page, cell_pointer_idx)
        inline_payload = page.body.cell_pointers[cell_pointer_idx].content.payload.inline_payload
        #payload_io = pysqlite3._parser.KaitaiStream(pysqlite3._parser.BytesIO(inline_payload))
        payload_io = pysqlite3._parser.KaitaiStream(payload_reader)
        header_size = pysqlite3._parser.vlq_base128_be.VlqBase128Be(payload_io)
        if _debug:
            # header size is part of the header
            header_positions = payload_reader._last_read_positions
        # TODO avoid buffering. call RecordHeader with (io, size), so it can read to "eos" (end of stream)
        _raw_header = payload_io.read_bytes((header_size.value - 1))
        _raw_header_io = pysqlite3._parser.KaitaiStream(pysqlite3._parser.BytesIO(_raw_header))
        #print("raw payload header", _raw_header)
        header = pysqlite3._parser.Sqlite3.RecordHeader(_raw_header_io, db, db._root)
        if _debug:
            header_positions += payload_reader._last_read_positions
            print("header_positions", header_positions)
            #print("payload header", header, dir(header))
            #print("payload header.value_types", header.value_types, dir(header.value_types))
        #value_offset = header_size.value
        result = []
        for value_type_idx, value_type in enumerate(header.value_types):
            # value_type is SerialType
            if _debug:
                #print(f"payload header.value_types[{value_type_idx}]", value_type, dir(value_type))
                #print(f"payload header.value_types[{value_type_idx}].raw_value.value", value_type.raw_value.value)
                print(f"payload header.value_types[{value_type_idx}].type", value_type.type)
            value_size = 0
            size_of_type = [0, 1, 2, 3, 4, 6, 8, 8, 0, 0]
            if value_type.raw_value.value >= 12:
                value_size = value_type.len_blob_string
            else:
                value_size = size_of_type[value_type.raw_value.value]

            if _debug:
                print(f"payload header.value_types[{value_type_idx}] value_size", value_size)

            #value_bytes = payload_io.read_bytes(value_size)
            #result.append(value_bytes)

            value = parser_sqlite3.Sqlite3.Value(value_type, payload_io, db, db._root)

            print("value.value:", value.value, dir(value.value))

            if value_type.raw_value.value == 0:
                # value is NULL
                #value = None
                value = row_id
            else:
                value = value.value.value

            result.append(value)

            if _debug:
                value_positions = payload_reader._last_read_positions
                print("value_positions", value_positions)

                print(f"payload values[{value_type_idx}]: {value_bytes[0:100]}...")
                print(f"payload values[{value_type_idx}] md5: {hashlib.md5(value_bytes).hexdigest()}")
                #value_offset += value_size

            # type nil can mean: this column is indexed
            # example: CREATE TABLE "table" ("key" INTEGER, "value" TEXT, PRIMARY KEY("key"))
            # -> the column "key" has type nil
            # -> the columns "key" and "value" are stored in table cells
            # -> value of "key" is in the row_id -> page.body.cell_pointers[cell_pointer_idx].content.row_id.value

            """
            if value_type.type == pysqlite3._parser.Sqlite3.Serial.blob:
                print(f"payload header.value_types[{value_type_idx}].len_blob_string", value_type.len_blob_string)
                value_size = value_type.len_blob_string
                pass
            elif value_type.type == pysqlite3._parser.Sqlite3.Serial.string_utf8:
                print(f"payload header.value_types[{value_type_idx}].len_blob_string", value_type.len_blob_string)
                value_size = value_type.len_blob_string
                pass
            elif value_type.type == pysqlite3._parser.Sqlite3.Serial.string_utf16_le:
                print(f"payload header.value_types[{value_type_idx}].len_blob_string", value_type.len_blob_string)
                value_size = value_type.len_blob_string
                pass
            elif value_type.type == pysqlite3._parser.Sqlite3.Serial.string_utf16_be:
                print(f"payload header.value_types[{value_type_idx}].len_blob_string", value_type.len_blob_string)
                value_size = value_type.len_blob_string
                pass
            else:
            """

            # null = 0
            # two_comp_8 = 1
            # two_comp_16 = 2
            # two_comp_24 = 3
            # two_comp_32 = 4
            # two_comp_48 = 5
            # two_comp_64 = 6
            # ieee754_64 = 7
            # integer_0 = 8
            # integer_1 = 9
            # internal_1 = 10
            # internal_2 = 11
            # blob = 12
            # string_utf8 = 13
            # string_utf16_le = 14
            # string_utf16_be = 15

            #print(f"payload header.value_types[{value_type_idx}].type.name", value_type.type.named)
            #print(f"payload header.value_types[{value_type_idx}].type.value", value_type.type.value)

        if _debug:
            #print("page.body.cell_pointers[cell_pointer_idx].content.payload.inline_payload", page.body.cell_pointers[cell_pointer_idx].content.payload.inline_payload, dir(page.body.cell_pointers[cell_pointer_idx].content.payload.inline_payload))
            print(f"page.body.cell_pointers[{cell_pointer_idx}].content.payload.inline_payload # 0:100", page.body.cell_pointers[cell_pointer_idx].content.payload.inline_payload[0:100])
            print(f"page.body.cell_pointers[{cell_pointer_idx}].content.payload.inline_payload # len", len(page.body.cell_pointers[cell_pointer_idx].content.payload.inline_payload))
            #print("page.body.cell_pointers[cell_pointer_idx].content.payload.first_overflow_page_number", page.body.cell_pointers[cell_pointer_idx].content.payload.first_overflow_page_number, dir(page.body.cell_pointers[cell_pointer_idx].content.payload.first_overflow_page_number))
            print(f"page.body.cell_pointers[{cell_pointer_idx}].content.payload.first_overflow_page_number.page_number", page.body.cell_pointers[cell_pointer_idx].content.payload.first_overflow_page_number.page_number)
            #print("page.body.cell_pointers[cell_pointer_idx].content.payload.first_overflow_page_number.page", page.body.cell_pointers[cell_pointer_idx].content.payload.first_overflow_page_number.page)

        return result

        # TODO remove? paging is implemented in payload_reader

        # go to next page
        page = page.body.cell_pointers[cell_pointer_idx].content.payload.first_overflow_page_number.page
        while page:
            # page is OverflowPage
            if _debug:
                #print("page", page, dir(page))
                # content: raw bytes
                #print("page.content", page.content, dir(page.content))
                print("page.content # len", len(page.content))
                #if hasattr(page, "next_page_number"): # always true
                if page.next_page_number.page:
                    #print("page.next_page_number", page.next_page_number, dir(page.next_page_number))
                    print("page.next_page_number.page_number", page.next_page_number.page_number)
                    #print("page.next_page_number.page", page.next_page_number.page, dir(page.next_page_number.page))
            page = page.next_page_number.page
    else:
        # payload is **not** overflow_record
        raise NotImplementedError


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

    raise NotImplementedError

    last_num = exec([
        sqlite3_exe,
        dbfile,
        "select num from subz order by num desc limit 1;"
    ])
    last_num = int(last_num)
    print(f"last num: {last_num}")

    num = 2
    values = get_values(num)
    print("values", values)
    return

    for num in range(1, 1 + last_num):
        get_values(num)
        break # debug

main()
