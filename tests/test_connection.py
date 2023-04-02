import os
import sqlite3

import pysqlite3


def create_test_db(database="test.db"):
    """
    use the native sqlite3 module to create the test database
    """
    try:
        os.unlink(database)
    except FileNotFoundError:
        pass
    con = sqlite3.connect(database)
    cur = con.cursor()

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

    con.commit()
    con.close()


def test_connection():
    create_test_db()

    con = pysqlite3.connect("test.db")
    # con = pysqlite3.connect(":memory:")

    print(f"page size: {con._db.header.page_size} bytes")
    print(
        f"db size: {con._db.header.num_pages} pages",
    )
    # FIXME "index" should be "number" because it is 1-based (?)
    print(f"idx_lock_byte_page: {con._db.header.idx_lock_byte_page}")
    print(f"idx_first_ptrmap_page: {con._db.header.idx_first_ptrmap_page}")
    print(f"idx_last_ptrmap_page: {con._db.header.idx_last_ptrmap_page}")

    print(f"con._db.pages =", con._db.pages)
    print(f"len(con._db.pages) =", len(con._db.pages))
    print(f"con._db.pages[0] =", con._db.pages[0])
    print(f"con._db.pages[0].page_number =", con._db.pages[0].page_number)
    print(f"con._db.pages[len-1] =", con._db.pages[len(con._db.pages)-1])
    print(f"con._db.pages[len-1].page_number =", con._db.pages[len(con._db.pages)-1].page_number)
    print(f"con._db.pages[-1] =", con._db.pages[-1])
    print(f"con._db.pages[-1].page_number =", con._db.pages[-1].page_number)
    print(f"con._root_page_numbers =", con._root_page_numbers)

    print("tables =", con._tables)

    print("con._columns")
    for table in con._tables:
        print(f"table {table}: columns =", con._columns(table))

    print("con._row_values")
    for table in con._tables:
        for row_id, values in enumerate(con._row_values(table)):
            print(f"table {table}: row {row_id + 1} =", values)

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
