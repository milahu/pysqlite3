from .connection import Connection
from .cursor import Cursor
from .row import Row
from .blob import Blob
from .prepare_protocol import PrepareProtocol


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

apilevel = "2.0"
paramstyle = "qmark"

sqlite_version = "3.40.1"
sqlite_version_info = (3, 40, 1)

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
