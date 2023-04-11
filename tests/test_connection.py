import os
import sqlite3
import hashlib

import pysqlite3


def create_test_db(database="test.db"):
    """
    use the native sqlite3 module to create the test database
    """
    print()
    try:
        os.unlink(database)
    except FileNotFoundError:
        pass
    # problem: we cannot set the page size in python's sqlite interface
    # workaround: use the native sqlite CLI tool to create the database
    con = sqlite3.connect(database)
    cur = con.cursor()

    # page_size must be one of: 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536 bytes.
    # use smallest page size to maximize fragmentation of blobs across pages
    # fragmented data is harder to parse
    # https://www.sqlite.org/pragma.html#pragma_page_size
    # https://www.oreilly.com/library/view/using-sqlite/9781449394592/re194.html
    page_size = 512
    cur.executescript(f"PRAGMA page_size = {page_size}; VACUUM;")

    cur.execute("CREATE TABLE IF NOT EXISTS lang(name, first_appeared)")
    data = [
        ("C++", 1985),
        ("Objective-C", 1984),
    ]
    cur.executemany("INSERT INTO lang(name, first_appeared) VALUES(?, ?)", data)

    # TODO set column types
    cur.execute("CREATE TABLE IF NOT EXISTS table2(column1, column2)")
    data = []
    for i in range(1, 10 + 1):
        data.append((f"row{i}_column1", f"row{i}_column2"))
    cur.executemany("INSERT INTO table2(column1, column2) VALUES(?, ?)", data)

    # TODO set column types
    cur.execute("CREATE TABLE IF NOT EXISTS blob_table(id INTEGER, md5 TEXT, value BLOB)")
    data = []
    # 7 keys per page. 21 keys = 3 pages
    num_rows = 255
    blob_size = page_size # always overflow
    #blob_size = page_size // 2 # always fit on page
    for i in range(1, num_rows + 1):
        _byte = i.to_bytes(1, "big")
        #print(f"inserting into blob_table: id={i} value[0]=0x{_byte.hex()}")
        value = blob_size * _byte
        md5 = hashlib.md5(value).hexdigest()
        data = (i, md5, value)
        cur.execute("INSERT INTO blob_table(id, md5, value) VALUES(?, ?, ?)", data)
    res = cur.execute("SELECT count() FROM blob_table")
    assert res.fetchone()[0] == num_rows

    con.commit()
    con.close()


def test_connection():
    database = "test.db"
    create_test_db(database)
    con = pysqlite3.connect(database)
    # con = pysqlite3.connect(":memory:")

    # ro: open in read-only mode
    sqlite_con = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    sqlite_cur = sqlite_con.cursor()

    print(f"page size: {con._db.header.page_size} bytes")
    print(
        f"db size: {con._db.header.num_pages} pages",
    )
    # FIXME "index" should be "number" because it is 1-based (?)
    print(f"idx_lock_byte_page: {con._db.header.idx_lock_byte_page}")
    print(f"idx_first_ptrmap_page: {con._db.header.idx_first_ptrmap_page}")
    print(f"idx_last_ptrmap_page: {con._db.header.idx_last_ptrmap_page}")

    print(f"con._db.pages =", con._db.pages)
    """
    # db.pages was removed for lazy parsing
    print(f"len(con._db.pages) =", len(con._db.pages))
    print(f"con._db.pages[0] =", con._db.pages[0])
    print(f"con._db.pages[0].page_number =", con._db.pages[0].page_number)
    print(f"con._db.pages[len-1] =", con._db.pages[len(con._db.pages)-1])
    print(f"con._db.pages[len-1].page_number =", con._db.pages[len(con._db.pages)-1].page_number)
    print(f"con._db.pages[-1] =", con._db.pages[-1])
    print(f"con._db.pages[-1].page_number =", con._db.pages[-1].page_number)
    """

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
            if table == "blob_table":
                # verify md5
                expected_md5 = hashlib.md5(values[2]).hexdigest()
                assert values[1] == expected_md5
        num_rows_expected = sqlite_cur.execute(f"SELECT count() FROM {table}").fetchone()[0]
        assert num_rows == num_rows_expected, f"num_rows: expected {num_rows_expected}, actual {num_rows}"

    raise NotImplementedError

    print("con._row_locations")
    for table in con._tables:
        for row_id, locations in enumerate(con._row_locations(table)):
            print(f"table {table}: locations {row_id + 1} =", locations)
            # f = open("test.con., "rb"); f.seek(8190); struct.unpack(">h", f.read(2))[0]

    db = con._db

    #for page_idx, page in enumerate(db.pages):
    if False:
        page_position = page_idx * db.header.page_size
        print(f"db.pages[{page_idx}] position = {page_position}")
        assert page.page_type.value == 0x0D  # Table B-Tree Leaf Cell (header 0x0d):
        for cell_idx, cell in enumerate(page.cells):
            print(
                f"db.pages[{page_idx}].cells[{cell_idx}].content.row_id.value =",
                cell.content.row_id.value,
            )
            # content_offset is relative to page
            print(
                f"db.pages[{page_idx}].cells[{cell_idx}].content_offset =",
                cell.content_offset,
            )
            payload_size = cell.content.p.value
            # payload.header.value_types looks rather useless...?
            # for value_type_idx, value_type in enumerate(cell.content.payload.header.value_types):
            if False:
                # print(f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.header.value_types[{value_type_idx}].value_type =", con._type_names[value_type.value_type])
                # if value_type.content_size != None:
                #    print(f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.header.value_types[{value_type_idx}].content_size =", value_type.content_size)
                if value_type.value_type == con._type_string:
                    print(
                        f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.header.value_types[{value_type_idx}].value.value = {repr(value_type.value.value)}"
                    )
                elif value_type.value_type == con._type_blob:
                    # TODO verify
                    print(
                        f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.header.value_types[{value_type_idx}].value.value = {repr(value_type.value.value)}"
                    )
                else:
                    # TODO verify
                    print(
                        f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.header.value_types[{value_type_idx}].value = {repr(value_type.value)}"
                    )
            for value_idx, value in enumerate(cell.content.payload.values):
                # print(f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.values[{value_idx}].serial_type.value_type = {con._type_names[value.serial_type.value_type]}")
                # if value.serial_type.content_size != None:
                #    print(f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.values[{value_idx}].serial_type.content_size = {value.serial_type.content_size}")
                if value.serial_type.value_type == con._type_string:
                    print(
                        f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.values[{value_idx}].value.value = {repr(value.value.value)}"
                    )
                elif value.serial_type.value_type == con._type_blob:
                    # TODO verify
                    print(
                        f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.values[{value_idx}].value.value = {repr(value.value.value)}"
                    )
                else:
                    # TODO verify
                    print(
                        f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.values[{value_idx}].value = {repr(value.value)}"
                    )
            print()
        # break # debug: stop after first page

    #raise SystemExit
    raise NotImplementedError

    cur = con.cursor()

    """
    cur.execute("CREATE TABLE lang(name, first_appeared)")
    data = [
        ("C++", 1985),
        ("Objective-C", 1984),
    ]
    cur.executemany("INSERT INTO lang(name, first_appeared) VALUES(?, ?)", data)
    # The INSERT statement implicitly opens a transaction
    con.commit()
    """

    # Print the table contents
    for row in cur.execute("SELECT name, first_appeared FROM lang"):
        print(row)

    print("I just deleted", cur.execute("DELETE FROM lang").rowcount, "rows")

    res = cur.execute("SELECT name FROM sqlite_master")
    print(res.fetchone())

    # con.rollback() # rollback a transaction

    # con.text_factory = str
    # con.text_factory = bytes
    # A callable that accepts a bytes parameter and returns a text representation of it.
    # The callable is invoked for SQLite values with the TEXT data type.
    # By default, this attribute is set to str.
    # If you want to return bytes instead, set text_factory to bytes.

    # con.total_changes
    # Return the total number of database rows that have been modified, inserted, or deleted since the database connection was opened.

    con.close()
