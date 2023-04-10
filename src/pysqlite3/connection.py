from .parser import sqlite3 as parser_sqlite3
from .parser import sqlite3_helpers as parser_sqlite3_helpers
from .cursor import Cursor
from .row import Row

import os
import math

import sqlglot

# TODO connection context manager
# TODO con = sqlite3.connect(":memory:")
# TODO shortcut methods: con.execute, etc


_debug = False


class Connection:

    in_transaction = False

    # the default is "", which is an alias for "DEFERRED".
    isolation_level = ""

    row_factory = Row

    text_factory = str  # decode strings with utf8
    # text_factory = bytes # keep strings as raw bytes

    total_changes = 0

    _db = None

    # https://www.sqlite.org/fileformat.html
    # Serial Type Codes Of The Record Format
    _type_names = [
        "null",
        # big-endian twos-complement integers
        "int8",
        "int16",
        "int24",
        "int32",
        "int48",
        "int64",
        # big-endian IEEE 754-2008 64-bit floating point number
        "float64",
        # the integer 0. (Only available for schema format 4 and higher.)
        # aka "false"?
        "int0",
        # the integer 1. (Only available for schema format 4 and higher.)
        # aka "true"?
        "int1",
        # Reserved for internal use
        "internal10",
        "internal11",
        # Value is a BLOB that is (N-12)/2 bytes in length.
        "blob",
        # Value is a string in the text encoding and (N-13)/2 bytes in length.
        # The nul terminator is not stored.
        "string",
    ]

    _type_null = 0
    _type_int8 = 1
    _type_int16 = 2
    _type_int24 = 3
    _type_int32 = 4
    _type_int48 = 5
    _type_int64 = 6
    _type_float64 = 7
    _type_int0 = 8
    _type_int1 = 9
    _type_internal10 = 10
    _type_internal11 = 11
    _type_blob = 12
    _type_string = 13

    def __init__(
        self,
        database,
        timeout=5.0,
        detect_types=0,
        isolation_level="DEFERRED",
        check_same_thread=True,
        cached_statements=128,
        uri=False,
        # non-standard args:
        allow_bad_size=False,
        **kwargs,
    ):
        if isolation_level != "DEFERRED":
            # TODO validate
            self.isolation_level = isolation_level

        if database == ":memory:":
            raise NotImplementedError

        db = parser_sqlite3.Sqlite3.from_file(database)
        self._db = db

        # monkeypatch db.pages
        def _parse_page(self, page_number):
            #page = self._db.pages[0]
            db = self._db
            _pos = db._io.pos()
            db._io.seek((page_number - 1) * db.header.page_size)
            page = parser_sqlite3.Sqlite3.Page(1, 0, db._io, db, db._root)
            db._io.seek(_pos)
            return page

        # AttributeError: can't set attribute 'pages'
        #db.pages = parser_sqlite3_helpers.PagesList(db)
        db._m_pages = parser_sqlite3_helpers.PagesList(db)

        # page size
        # Must be a power of two between 512 and 32768 inclusive,
        # or the value 1 representing a page size of 65536.
        # validate page size
        page_size_base = math.log(db.header.page_size, 2)
        if int(page_size_base) != page_size_base:
            raise Exception(f"page size must be a power of 2: {db.header.page_size}")
        if db.header.page_size < 512 or 32768 < db.header.page_size:
            raise Exception(
                f"page size must be in range (512, 32768): {db.header.page_size}"
            )

        if database != ":memory:":
            expected_size = db.header.page_size * db.header.num_pages
            actual_size = os.path.getsize(database)
            if actual_size != expected_size:
                # this is a fatal error in the original implementation
                msg = f"bad size. expected {expected_size}. actual {actual_size}"
                if allow_bad_size:
                    print(f"warning: {msg}")
                else:
                    raise Exception(msg)

    def cursor(self, factory=Cursor):
        cur = factory(self)
        return cur

    def blobopen(self, table, column, row, /, *, readonly=False, name="main"):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def execute(self, sql, parameters=(), /):
        raise NotImplementedError

    def executemany(self, sql, parameters, /):
        raise NotImplementedError

    def executescript(sql_script, /):
        raise NotImplementedError

    def create_function(name, narg, func, *, deterministic=False):
        raise NotImplementedError

    def create_aggregate(name, /, n_arg, aggregate_class):
        raise NotImplementedError

    def create_window_function(name, num_params, aggregate_class, /):
        raise NotImplementedError

    def create_collation(name, callable):
        raise NotImplementedError

    def interrupt(self):
        raise NotImplementedError

    def set_authorizer(authorizer_callback):
        raise NotImplementedError

    def set_progress_handler(progress_handler, n):
        raise NotImplementedError

    def set_trace_callback(trace_callback):
        raise NotImplementedError

    def enable_load_extension(enabled, /):
        raise NotImplementedError

    def load_extension(path, /):
        raise NotImplementedError

    def iterdump(self):
        raise NotImplementedError

    def backup(self, target, *, pages=-1, progress=None, name="main", sleep=0.250):
        raise NotImplementedError

    def getlimit(self, category, /):
        raise NotImplementedError

    def setlimit(self, category, limit, /):
        raise NotImplementedError

    def serialize(*, name="main"):
        raise NotImplementedError

    def deserialize(self, data, /, *, name="main"):
        raise NotImplementedError

    @property
    def _tables(self):
        """
        get all table names

        non-standard method

        https://www.sqlite.org/fileformat.html
        2.6. Storage Of The SQL Database Schema

        Page 1 of a database file is the root page of a table b-tree
        that holds a special table named "sqlite_schema".
        This b-tree is known as the "schema table"
        since it stores the complete database schema.

        The structure of the sqlite_schema table is
        as if it had been created using the following SQL:

        CREATE TABLE sqlite_schema(
            type text,
            name text,
            tbl_name text,
            rootpage integer,
            sql text
        );

        The sqlite_schema.tbl_name column holds the name of a table or view
        that the object is associated with.
        For a table or view, the tbl_name column is a copy of the name column.
        For an index, the tbl_name is the name of the table that is indexed.
        For a trigger, the tbl_name column stores the name of the table or view
        that causes the trigger to fire.
        """
        tables = []
        page = self._db.pages[0]
        assert page.page_type.value == 0x0D  # Table B-Tree Leaf Cell
        for cell_idx, cell in enumerate(page.cell_pointers):
            values = cell.content.payload.values
            if values[0].value.value == "table":
                tables.append(values[1].value.value)
        return tables

    def _schema(self, table):
        """
        get the SQL schema of a table

        non-standard method
        """
        page = self._db.pages[0]
        assert page.page_type.value == 0x0D  # Table B-Tree Leaf Cell
        for cell_idx, cell in enumerate(page.cell_pointers):
            values = cell.content.payload.values
            if values[0].value.value == "table" and values[1].value.value == table:
                sql = values[4].value.value
                return sql
        return None

    def _columns(self, table):
        """
        get all column names of a table

        non-standard method
        """
        page = self._db.pages[0]
        assert page.page_type.value == 0x0D  # Table B-Tree Leaf Cell
        for cell_idx, cell in enumerate(page.cell_pointers):
            values = cell.content.payload.values
            if values[0].value.value == "table" and values[1].value.value == table:
                sql = values[4].value.value
                tree = sqlglot.parse_one(sql, read="sqlite")
                columns = [id.name for id in tree.find_all(sqlglot.exp.ColumnDef)]
                if len(columns) == 0:
                    # FIXME try other sql parsers: sqlparse, sqltree
                    raise NotImplementedError(f"table has untyped columns: {sql}")
                return columns
        return None

    def _column_types(self, table):
        """
        get all column types of a table

        non-standard method
        """
        raise NotImplementedError
        # TODO parse sql in self._db.pages[0]

    def _rootpage_num(self, table):
        """
        get the rootpage number of a table

        non-standard method
        """
        page = self._db.pages[0]
        assert page.page_type.value == 0x0D  # Table B-Tree Leaf Cell
        for cell_idx, cell in enumerate(page.cell_pointers):
            values = cell.content.payload.values
            if values[0].value.value == "table" and values[1].value.value == table:
                return values[3].value
        return None

    @property
    def _table_page_numbers(self):
        """
        get the page numbers of all tables,
        excluding the sqlite_schema table in page 1

        non-standard method
        """
        page = self._db.pages[0]
        assert page.page_type.value == 0x0D  # Table B-Tree Leaf Cell
        for cell in page.cell_pointers:
            yield cell.content.payload.values[3].value

    '''
    wrong?
    TODO root page numbers are stored in the database schema?
    = root page numbers of table-trees and index-trees
    @property
    def _root_page_numbers(self):
        """
        get the page numbers of all root pages,
        excluding page 1

        non-standard method
        """
        if self._db.header.num_pages == 1:
            return []
        i = 1 # page 2
        i_max = self._db.header.num_pages - 1
        while i < i_max: # `i == i_max` means "end of file"
            print("_root_page_numbers: i =", i)
            page = self._db.pages[i]
            print("_root_page_numbers: page =", page, dir(page))
            yield page.page_number
            # go to next root page
            if hasattr(page, "rightmost_page_pointer"):
                i = page.rightmost_page_pointer.page_number - 1
            else:
                i = i + 1
    '''

    def _table_values(self, table):
        """
        get all values of a table

        non-standard method
        """
        root_page_idx = self._rootpage_num(table) - 1
        assert root_page_idx != None
        print("con._table_values: table", table)
        print("con._table_values: root_page_idx", root_page_idx)
        #assert page.page_type.value == 0x0D, f"expected page type 0x0D, actual 0x{page.page_type.value:02X}"

        # visit all values in order:
        #
        # - go to the leftmost leaf node, loop its values
        # - while the right-pointer is not null:
        #   - follow the right-pointer to the next leaf node, loop its values

        interior_page_stack = []
        interior_cell_idx_stack = []

        root_page = self._db.pages[root_page_idx]

        if root_page.page_type.value == 0x0D: # leaf page
            # tree is empty
            return

        interior_page_stack.append(root_page) # first page
        interior_cell_idx_stack.append(0) # first cell

        while interior_page_stack:

            interior_page = interior_page_stack[-1]
            interior_cell_idx = interior_cell_idx_stack[-1]

            cell_pointer = interior_page.cell_pointers[interior_cell_idx]
            page_idx = cell_pointer.content.left_child_page_pointer.page_number - 1
            page = self._db.pages[page_idx]

            # Left: Recursively traverse the current node's left subtree.
            while page.page_type.value == 0x05: # interior page
                interior_page = page
                interior_page_stack.append(interior_page)
                interior_cell_idx = 0 # first cell
                interior_cell_idx_stack.append(interior_cell_idx)

                cell_pointer = interior_page.cell_pointers[interior_cell_idx]
                page_idx = cell_pointer.content.left_child_page_pointer.page_number - 1
                page = self._db.pages[page_idx]

            # Node: Visit the current node.
            # loop cells, yield all values
            assert page.page_type.value == 0x0D # leaf page
            leaf_page = page
            #print(f"interior cell {interior_cell_idx}: con._table_values: page.num_cell_pointers", page.num_cell_pointers)
            for cell_pointer_idx, cell_pointer in enumerate(leaf_page.cell_pointers):
                # cell_pointer.content is TableLeafCell
                #print(f"interior cell {interior_cell_idx}: cell {cell_pointer_idx}: cell_pointer.content", cell_pointer.content, dir(cell_pointer.content))
                row_id = cell_pointer.content.row_id.value
                values = []
                # TODO memleak? cell_pointer.content
                if hasattr(cell_pointer.content.payload, "values"):
                    # non-overflow record
                    for value in cell_pointer.content.payload.values:
                        if value.serial_type.type.value == 0:
                            # null
                            # TODO verify. does "null" always mean row_id?
                            values.append(row_id)
                        elif value.serial_type.type.value >= 12:
                            # blob or string
                            values.append(value.value.value)
                        else:
                            # int or float or bool
                            values.append(value.value)
                    yield values
                else:
                    # overflow record
                    assert hasattr(cell_pointer.content.payload, "inline_payload")
                    # payload is overflow_record
                    # must be parsed manually because paging
                    if _debug:
                        print(f"page.body.cell_pointers[{cell_pointer_idx}].content.payload.inline_payload_size", cell.content.payload.inline_payload_size)
                    # inline_payload: header + body
                    # we must parse this manually because paging
                    con = self
                    db = con._db
                    payload_reader = parser_sqlite3_helpers.PayloadReader(db, leaf_page, cell_pointer_idx)
                    inline_payload = cell_pointer.content.payload.inline_payload
                    #payload_io = parser_sqlite3.KaitaiStream(parser_sqlite3.BytesIO(inline_payload))
                    payload_io = parser_sqlite3.KaitaiStream(payload_reader)
                    header_size = parser_sqlite3.vlq_base128_be.VlqBase128Be(payload_io)
                    if _debug:
                        # header size is part of the header
                        header_positions = payload_reader._last_read_positions
                    # TODO avoid buffering. call RecordHeader with (io, size), so it can read to "eos" (end of stream)
                    _raw_header = payload_io.read_bytes((header_size.value - 1))
                    _raw_header_io = parser_sqlite3.KaitaiStream(parser_sqlite3.BytesIO(_raw_header))
                    #print("raw payload header", _raw_header)
                    header = parser_sqlite3.Sqlite3.RecordHeader(_raw_header_io, db, db._root)
                    if _debug:
                        header_positions += payload_reader._last_read_positions
                        print("header_positions", header_positions)
                        #print("payload header", header, dir(header))
                        #print("payload header.value_types", header.value_types, dir(header.value_types))
                    #value_offset = header_size.value
                    values = []
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
                        if value.serial_type.type.value == 0:
                            # null
                            # TODO verify. does "null" always mean row_id?
                            values.append(row_id)
                        elif value.serial_type.type.value >= 12:
                            # blob or string
                            values.append(value.value.value)
                        else:
                            # int or float or bool
                            values.append(value.value)
                        if _debug:
                            value_positions = payload_reader._last_read_positions
                            print("value_positions", value_positions)

                            print(f"payload values[{value_type_idx}]: {value_bytes[0:100]}...")
                            print(f"payload values[{value_type_idx}] md5: {hashlib.md5(value_bytes).hexdigest()}")
                            #value_offset += value_size
                    yield tuple(values)

            # Right: Recursively traverse the current node's right subtree.
            all_done = False
            while interior_cell_idx == interior_page.num_cell_pointers - 1:
                # cell is rightmost cell -> go up
                interior_page_stack.pop()
                interior_cell_idx_stack.pop()
                if not interior_page_stack:
                    all_done = True
                    break # no more parents -> stop traversal
                interior_page = interior_page_stack[-1]
                interior_cell_idx = interior_cell_idx_stack[-1]
            if all_done:
                break
            interior_cell_idx_stack[-1] += 1 # go right

    def _size_of_raw_type(self, raw_type):
        """
        https://www.sqlite.org/fileformat.html
        Serial Type Codes Of The Record Format
        """
        if raw_type >= 12: # string or blob
            if raw_type % 2 == 0: # blob
                return (raw_type - 12) >> 1 # bitshift to keep integer type
            return (raw_type - 13) >> 1
        sizes = [0, 1, 2, 3, 4, 6, 8, 8, 0, 0]
        return sizes[raw_type] # throws IndexError on invalid raw_type

    def _row_locations(self, table):
        """
        get all row locations of a table

        location = (start, size)

        start is the absolute index in the database file

        non-standard method
        """
        page_idx = self._rootpage_num(table) - 1
        assert page_idx != None
        page = self._db.pages[page_idx] # FIXME random access
        #assert page.page_type.value == 0x0D  # Table B-Tree Leaf Cell
        while page:
            page_position = page_idx * self._db.header.page_size

            if page.page_type.value == 0x05:
                for cell_idx, cell in enumerate(page.cell_pointers):
                    print()
                    print("con._row_locations: page.page_number", page.page_number)
                    # cell.content is TableInteriorCell
                    # Interior pages of table b-trees have no payload
                    #print("con._row_locations: cell.content", cell.content, dir(cell.content))
                    # BtreePagePointer
                    #print("con._row_locations: cell.content.left_child_page_pointer", cell.content.left_child_page_pointer, dir(cell.content.left_child_page_pointer))
                    # int
                    print("con._row_locations: cell.content.left_child_page_pointer.page_number", cell.content.left_child_page_pointer.page_number)
                    # int
                    print("con._row_locations: cell.content.row_id.value", cell.content.row_id.value)
                    #raise NotImplementedError
                    # go to next page
                    page_idx = cell.content.left_child_page_pointer.page_number - 1
                    if page_idx >= self._db.header.num_pages: # done last page
                        page = None
                        break
                    # TODO this makes sense only for the last cell
                    # or is there always only one cell?
                    assert cell_idx == 0
                    page = self._db.pages[page_idx]

            elif page.page_type.value == 0x0D:
                for cell_idx, cell in enumerate(page.cell_pointers):
                    locations = []
                    # TODO why +5? header of cell? always 5?
                    last_value_end = page_position + cell.ofs_content + 5
                    for value in cell.content.payload.values:
                        start = last_value_end
                        size = self._size_of_raw_type(value.serial_type.raw_value.value)
                        locations.append((start, size))
                        last_value_end += size
                    yield locations

            page = None
            page_idx = None
            # TODO read more pages when necessary
