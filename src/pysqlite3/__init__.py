import datetime
import time
import collections.abc

from .connection import Connection
from .cursor import Cursor
from .row import Row
from .blob import Blob
from .prepare_protocol import PrepareProtocol

# from _sqlite3 import *
# from _sqlite3 import _deprecated_version


def connect(
    database,
    timeout=5.0,
    detect_types=0,
    isolation_level="DEFERRED",
    check_same_thread=True,
    factory=Connection,
    cached_statements=128,
    uri=False,
    # non-standard args:
    allow_bad_size=False,
    **kwargs,
):
    con = factory(
        database,
        timeout=timeout,
        detect_types=detect_types,
        isolation_level=isolation_level,
        check_same_thread=check_same_thread,
        cached_statements=cached_statements,
        uri=uri,
        # non-standard args:
        allow_bad_size=allow_bad_size,
        **kwargs,
    )
    return con


def complete_statement(statement):
    raise NotImplementedError


def enable_callback_tracebacks(flag, /):
    raise NotImplementedError


def register_adapter(type, adapter, /):
    raise NotImplementedError


def register_converter(typename, converter, /):
    raise NotImplementedError


PARSE_DECLTYPES = 1
PARSE_COLNAMES = 2

SQLITE_OK = 0
SQLITE_DENY = 1
SQLITE_IGNORE = 2

# _deprecated_version = ""
sqlite_version = "3.40.1"

# Single-thread mode
# Threads may not share the module
# SQLITE_THREADSAFE = 0
threadsafety = 0

# Multi-thread mode
# Threads may share the module, but not connections
# SQLITE_THREADSAFE = 2
# threadsafety = 1

# Serialized mode
# Threads may share the module, connections and cursors
# SQLITE_THREADSAFE = 1
# threadsafety = 2

version = "2.6.0"
version_info = (2, 6, 0)

# https://github.com/python/cpython/blob/main/Lib/sqlite3/dbapi2.py

_deprecated_names = frozenset({"version", "version_info"})

paramstyle = "qmark"

apilevel = "2.0"

Date = datetime.date

Time = datetime.time

Timestamp = datetime.datetime


def DateFromTicks(ticks):
    return Date(*time.localtime(ticks)[:3])


def TimeFromTicks(ticks):
    return Time(*time.localtime(ticks)[3:6])


def TimestampFromTicks(ticks):
    return Timestamp(*time.localtime(ticks)[:6])


# _deprecated_version_info = tuple(map(int, _deprecated_version.split(".")))
sqlite_version_info = tuple([int(x) for x in sqlite_version.split(".")])

Binary = memoryview
collections.abc.Sequence.register(Row)


def register_adapters_and_converters():
    return  # FIXME
    from warnings import warn

    msg = (
        "The default {what} is deprecated as of Python 3.12; "
        "see the sqlite3 documentation for suggested replacement recipes"
    )

    def adapt_date(val):
        warn(msg.format(what="date adapter"), DeprecationWarning, stacklevel=2)
        return val.isoformat()

    def adapt_datetime(val):
        warn(msg.format(what="datetime adapter"), DeprecationWarning, stacklevel=2)
        return val.isoformat(" ")

    def convert_date(val):
        warn(msg.format(what="date converter"), DeprecationWarning, stacklevel=2)
        return datetime.date(*map(int, val.split(b"-")))

    def convert_timestamp(val):
        warn(msg.format(what="timestamp converter"), DeprecationWarning, stacklevel=2)
        datepart, timepart = val.split(b" ")
        year, month, day = map(int, datepart.split(b"-"))
        timepart_full = timepart.split(b".")
        hours, minutes, seconds = map(int, timepart_full[0].split(b":"))
        if len(timepart_full) == 2:
            microseconds = int("{:0<6.6}".format(timepart_full[1].decode()))
        else:
            microseconds = 0

        val = datetime.datetime(year, month, day, hours, minutes, seconds, microseconds)
        return val

    register_adapter(datetime.date, adapt_date)
    register_adapter(datetime.datetime, adapt_datetime)
    register_converter("date", convert_date)
    register_converter("timestamp", convert_timestamp)


register_adapters_and_converters()

# Clean up namespace

del register_adapters_and_converters
