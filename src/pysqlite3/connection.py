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

    text_factory = str # decode strings with utf8
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
        print(f"page size: {db.len_page} bytes")
        print(
            f"db size: {db.num_pages} pages",
        )

        # page size
        # Must be a power of two between 512 and 32768 inclusive,
        # or the value 1 representing a page size of 65536.
        if db.len_page == 1:
            # FIXME db.len_page is read-only
            # db.len_page = 12345 # -> AttributeError: can't set attribute 'len_page'
            # db.len_page = 65536
            raise Exception("not implemented: db.len_page == 1")
        else:
            # validate page size
            page_size_base = math.log(db.len_page, 2)
            if int(page_size_base) != page_size_base:
                raise Exception(f"page size must be a power of 2: {db.len_page}")
            if db.len_page < 512 or 32768 < db.len_page:
                raise Exception(
                    f"page size must be in range (512, 32768): {db.len_page}"
                )

        if database != ":memory:":
            expected_size = db.len_page * db.num_pages
            actual_size = os.path.getsize(database)
            if actual_size != expected_size:
                # this is a fatal error in the original implementation
                msg = f"bad size. expected {expected_size}. actual {actual_size}"
                if allow_bad_size:
                    print(f"warning: {msg}")
                else:
                    raise Exception(msg)

        raise NotImplementedError

    def cursor(self, factory=Cursor):
        raise NotImplementedError

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
