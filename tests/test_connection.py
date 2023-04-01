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
