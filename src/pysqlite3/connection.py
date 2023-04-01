from .parser import sqlite3 as parser_sqlite3
from .cursor import Cursor
from .row import Row

import os
import math

# TODO connection context manager
# TODO con = sqlite3.connect(":memory:")
# TODO shortcut methods: con.execute, etc


class Connection:

    in_transaction = False

    # the default is "", which is an alias for "DEFERRED".
    isolation_level = ""

    row_factory = Row

    text_factory = str  # decode strings with utf8
    # text_factory = bytes # keep strings as raw bytes

    total_changes = 0

    _db = None

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

        # debug
        print(f"page size: {db.header.page_size} bytes")
        print(
            f"db size: {db.header.page_count} pages",
        )
        print()

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
            expected_size = db.header.page_size * db.header.page_count
            actual_size = os.path.getsize(database)
            if actual_size != expected_size:
                # this is a fatal error in the original implementation
                msg = f"bad size. expected {expected_size}. actual {actual_size}"
                if allow_bad_size:
                    print(f"warning: {msg}")
                else:
                    raise Exception(msg)

        # https://www.sqlite.org/fileformat.html
        # Serial Type Codes Of The Record Format
        type_names = [
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

        type_null = 0
        type_int8 = 1
        type_int16 = 2
        type_int24 = 3
        type_int32 = 4
        type_int48 = 5
        type_int64 = 6
        type_float64 = 7
        type_int0 = 8
        type_int1 = 9
        type_internal10 = 10
        type_internal11 = 11
        type_blob = 12
        type_string = 13

        for page_idx, page in enumerate(db.pages):
            page_position = page_idx * db.header.page_size
            print(f"db.pages[{page_idx}] position = {page_position}")
            assert page.page_type.value == 0x0d # Table B-Tree Leaf Cell (header 0x0d):
            for cell_idx, cell in enumerate(page.cells):
                print(f"db.pages[{page_idx}].cells[{cell_idx}].content.row_id.value =", cell.content.row_id.value)
                # content_offset is relative to page
                print(f"db.pages[{page_idx}].cells[{cell_idx}].content_offset =", cell.content_offset)
                payload_size = cell.content.p.value
                for value_type_idx, value_type in enumerate(cell.content.payload.header.value_types):
                    print(f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.header.value_types[{value_type_idx}].value_type =", type_names[value_type.value_type])
                    if value_type.content_size != None:
                        print(f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.header.value_types[{value_type_idx}].content_size =", value_type.content_size)
                    print()
                for value_idx, value in enumerate(cell.content.payload.values):
                    print(f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.values[{value_idx}].serial_type.value_type = {type_names[value.serial_type.value_type]}")
                    if value.serial_type.content_size != None:
                        print(f"db.pages[{page_idx}].cells[{cell_idx}].content.payload.values[{value_idx}].serial_type.content_size = {value.serial_type.content_size}")
                    if value.serial_type.value_type == type_string:
                        print(f"value[{value_idx}].value.value = {value.value.value}")
                    elif value.serial_type.value_type == type_blob:
                        # TODO verify
                        print(f"value[{value_idx}].value.value = {value.value.value}")
                    else:
                        # TODO verify
                        print(f"value[{value_idx}].value = {value.value}")
                    print()
                print()
            #break # debug: stop after first page
        raise SystemExit
        raise NotImplementedError

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
