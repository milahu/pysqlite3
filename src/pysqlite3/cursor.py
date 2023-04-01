from .row import Row


class Cursor:

    """
    Read/write attribute that controls the number of rows returned by fetchmany().
    The default value is 1 which means a single row would be fetched per call.
    """

    arraysize = 1

    """
    Read-only attribute that provides the SQLite database Connection
    belonging to the cursor.
    A Cursor object created by calling con.cursor()
    will have a connection attribute that refers to con:

    ```py
    con = sqlite3.connect(":memory:")
    cur = con.cursor()
    cur.connection == con # True
    ```
    """
    connection = None

    """
    Read-only attribute that provides the column names of the last query.
    To remain compatible with the Python DB API,
    it returns a 7-tuple for each column
    where the last six items of each tuple are None.

    It is set for SELECT statements without any matching rows as well.
    """
    description = None

    """
    Read-only attribute that provides the row id of the last inserted row.
    It is only updated after successful INSERT or REPLACE statements
    using the execute() method.
    For other statements, after executemany() or executescript(),
    or if the insertion failed, the value of lastrowid is left unchanged.
    The initial value of lastrowid is None.
    """
    lastrowid = None

    """
    Read-only attribute that provides the number of modified rows
    for INSERT, UPDATE, DELETE, and REPLACE statements;
    is -1 for other statements, including CTE queries.
    It is only updated by the execute() and executemany() methods.
    """
    rowcount = -1

    """
    Control how a row fetched from this Cursor is represented.
    If None, a row is represented as a tuple.
    Can be set to the included sqlite3.Row;
    or a callable that accepts two arguments,
    a Cursor object and the tuple of row values,
    and returns a custom object representing an SQLite row.

    Defaults to what Connection.row_factory was set to
    when the Cursor was created.
    Assigning to this attribute does not affect
    Connection.row_factory of the parent connection.

    See How to create and use row factories [1] for more details.

    [1]: https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory
    """
    row_factory = None

    def __init__(self, connection):
        self.connection = connection

    def execute(self, sql, parameters=(), /):
        """
        Execute SQL a single SQL statement,
        optionally binding Python values using placeholders.
        """
        raise NotImplementedError

    def executemany(self, sql, parameters, /):
        raise NotImplementedError

    def executescript(self, sql_script, /):
        raise NotImplementedError

    def fetchone(self):
        raise NotImplementedError

    def fetchmany(self, size=arraysize):
        raise NotImplementedError

    def fetchall(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def setinputsizes(self, sizes, /):
        raise NotImplementedError

    def setoutputsize(self, size, column=None, /):
        raise NotImplementedError
