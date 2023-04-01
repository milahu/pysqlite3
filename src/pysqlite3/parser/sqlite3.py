# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, "API_VERSION", (0, 9)) < (0, 9):
    raise Exception(
        "Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s"
        % (kaitaistruct.__version__)
    )

from . import vlq_base128_be


class Sqlite3(KaitaiStruct):
    """SQLite3 is a popular serverless SQL engine, implemented as a library
    to be used within other applications. It keeps its databases as
    regular disk files.

    Every database file is segmented into pages. First page (starting at
    the very beginning) is special: it contains a file-global header
    which specifies some data relevant to proper parsing (i.e. format
    versions, size of page, etc). After the header, normal contents of
    the first page follow.

    Each page would be of some type, and generally, they would be
    reached via the links starting from the first page. First page type
    (`root_page`) is always "btree_page".

    .. seealso::
       Source - https://www.sqlite.org/fileformat.html
    """

    class FormatVersion(Enum):
        legacy = 1
        wal = 2

    class BtreePageType(Enum):
        index_interior = 2
        table_interior = 5
        index_leaf = 10
        table_leaf = 13

    class PtrmapPageType(Enum):
        root_page = 1
        free_page = 2
        overflow1 = 3
        overflow2 = 4
        btree = 5

    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = Sqlite3.DatabaseHeader(self._io, self, self._root)

    class LockBytePage(KaitaiStruct):
        """The lock-byte page is the single page of the database file that contains the bytes at offsets between
        1073741824 and 1073742335, inclusive. A database file that is less than or equal to 1073741824 bytes
        in size contains no lock-byte page. A database file larger than 1073741824 contains exactly one
        lock-byte page.
        The lock-byte page is set aside for use by the operating-system specific VFS implementation in implementing
        the database file locking primitives. SQLite does not use the lock-byte page.
        """

        def __init__(self, page_number, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.page_number = page_number
            self._read()

        def _read(self):
            pass

    class FreelistTrunkPagePointer(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.page_number = self._io.read_u4be()

        @property
        def page(self):
            if hasattr(self, "_m_page"):
                return self._m_page

            if self.page_number != 0:
                io = self._root._io
                _pos = io.pos()
                io.seek(((self.page_number - 1) * self._root.header.page_size))
                self._raw__m_page = io.read_bytes(self._root.header.page_size)
                _io__raw__m_page = KaitaiStream(BytesIO(self._raw__m_page))
                self._m_page = Sqlite3.FreelistTrunkPage(
                    _io__raw__m_page, self, self._root
                )
                io.seek(_pos)

            return getattr(self, "_m_page", None)

    class BtreePage(KaitaiStruct):
        def __init__(self, page_number, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.page_number = page_number
            self._read()

        def _read(self):
            if self.page_number == 1:
                self.database_header = Sqlite3.DatabaseHeader(
                    self._io, self, self._root
                )

            self.page_type = KaitaiStream.resolve_enum(
                Sqlite3.BtreePageType, self._io.read_u1()
            )
            self.first_freeblock = self._io.read_u2be()
            self.cell_count = self._io.read_u2be()
            self.cell_content_area_start_raw = self._io.read_u2be()
            self.num_frag_free_bytes = self._io.read_u1()
            if (self.page_type == Sqlite3.BtreePageType.index_interior) or (
                self.page_type == Sqlite3.BtreePageType.table_interior
            ):
                self.right_ptr = Sqlite3.BtreePagePointer(self._io, self, self._root)

            self.cells = []
            for i in range(self.cell_count):
                self.cells.append(Sqlite3.CellPointer(self._io, self, self._root))

        @property
        def call_content_area_start(self):
            if hasattr(self, "_m_call_content_area_start"):
                return self._m_call_content_area_start

            self._m_call_content_area_start = (
                65536
                if self.cell_content_area_start_raw == 0
                else self.cell_content_area_start_raw
            )
            return getattr(self, "_m_call_content_area_start", None)

        @property
        def cell_content_area(self):
            if hasattr(self, "_m_cell_content_area"):
                return self._m_cell_content_area

            _pos = self._io.pos()
            self._io.seek(self.call_content_area_start)
            self._m_cell_content_area = self._io.read_bytes(
                (self._root.header.usable_size - self.call_content_area_start)
            )
            self._io.seek(_pos)
            return getattr(self, "_m_cell_content_area", None)

        @property
        def reserved_area(self):
            if hasattr(self, "_m_reserved_area"):
                return self._m_reserved_area

            if self._root.header.reserved_space != 0:
                _pos = self._io.pos()
                self._io.seek(
                    (self._root.header.page_size - self._root.header.reserved_space)
                )
                self._m_reserved_area = self._io.read_bytes_full()
                self._io.seek(_pos)

            return getattr(self, "_m_reserved_area", None)

    class BtreePagePointer(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.page_number = self._io.read_u4be()

        @property
        def page(self):
            if hasattr(self, "_m_page"):
                return self._m_page

            if self.page_number != 0:
                io = self._root._io
                _pos = io.pos()
                io.seek(((self.page_number - 1) * self._root.header.page_size))
                self._raw__m_page = io.read_bytes(self._root.header.page_size)
                _io__raw__m_page = KaitaiStream(BytesIO(self._raw__m_page))
                self._m_page = Sqlite3.BtreePage(
                    self.page_number, _io__raw__m_page, self, self._root
                )
                io.seek(_pos)

            return getattr(self, "_m_page", None)

    class OverflowPage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.next_page_number = Sqlite3.OverflowPagePointer(
                self._io, self, self._root
            )
            self.content = self._io.read_bytes((self._root.header.page_size - 4))

    class PtrmapEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = KaitaiStream.resolve_enum(
                Sqlite3.PtrmapPageType, self._io.read_u1()
            )
            self.page_number = self._io.read_u4be()

    class Int0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass

    class OverflowRecord(KaitaiStruct):
        def __init__(self, payload_size, x, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.payload_size = payload_size
            self.x = x
            self._read()

        def _read(self):
            self.inline_payload = self._io.read_bytes(
                (self.k if self.k <= self.x else self._root.header.m)
            )
            self.overflow_page_number = Sqlite3.OverflowPagePointer(
                self._io, self, self._root
            )

        @property
        def k(self):
            if hasattr(self, "_m_k"):
                return self._m_k

            self._m_k = self._root.header.m + (
                (self.payload_size - self._root.header.m)
                % (self._root.header.usable_size - 4)
            )
            return getattr(self, "_m_k", None)

    class FreelistTrunkPage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.next_page = Sqlite3.FreelistTrunkPagePointer(
                self._io, self, self._root
            )
            self.l = self._io.read_u4be()
            self.free_pages = []
            for i in range(self.l):
                self.free_pages.append(self._io.read_u4be())

    class PtrmapPage(KaitaiStruct):
        def __init__(self, page_number, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.page_number = page_number
            self._read()

        def _read(self):
            self.entries = []
            for i in range(self.entry_count):
                self.entries.append(Sqlite3.PtrmapEntry(self._io, self, self._root))

        @property
        def first_page(self):
            if hasattr(self, "_m_first_page"):
                return self._m_first_page

            self._m_first_page = 3 + (self._root.header.j * (self.page_number - 2))
            return getattr(self, "_m_first_page", None)

        @property
        def last_page(self):
            if hasattr(self, "_m_last_page"):
                return self._m_last_page

            self._m_last_page = (self.first_page + self._root.header.j) - 1
            return getattr(self, "_m_last_page", None)

        @property
        def entry_count(self):
            if hasattr(self, "_m_entry_count"):
                return self._m_entry_count

            self._m_entry_count = (
                (
                    self._root.header.page_count
                    if self.last_page > self._root.header.page_count
                    else self.last_page
                )
                - self.first_page
            ) + 1
            return getattr(self, "_m_entry_count", None)

    class StringUtf16Be(KaitaiStruct):
        def __init__(self, length, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.length = length
            self._read()

        def _read(self):
            self.value = (self._io.read_bytes(self.length)).decode("UTF-16BE")

    class NullValue(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass

    class Int1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass

    class OverflowPagePointer(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.page_number = self._io.read_u4be()

        @property
        def page(self):
            if hasattr(self, "_m_page"):
                return self._m_page

            if self.page_number != 0:
                io = self._root._io
                _pos = io.pos()
                io.seek(((self.page_number - 1) * self._root.header.page_size))
                self._raw__m_page = io.read_bytes(self._root.header.page_size)
                _io__raw__m_page = KaitaiStream(BytesIO(self._raw__m_page))
                self._m_page = Sqlite3.OverflowPage(_io__raw__m_page, self, self._root)
                io.seek(_pos)

            return getattr(self, "_m_page", None)

    class SerialType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.code = vlq_base128_be.VlqBase128Be(self._io)

        @property
        def value_type(self):
            if hasattr(self, "_m_value_type"):
                return self._m_value_type

            self._m_value_type = (
                (
                    12
                    if (self.code.value % 2) == 0
                    else ((13 + self._root.header.text_encoding) - 1)
                )
                if self.code.value >= 12
                else self.code.value
            )
            return getattr(self, "_m_value_type", None)

        @property
        def content_size(self):
            if hasattr(self, "_m_content_size"):
                return self._m_content_size

            if self.code.value >= 12:
                self._m_content_size = (self.code.value - 12) // 2

            return getattr(self, "_m_content_size", None)

    class IndexLeafCell(KaitaiStruct):
        """
        .. seealso::
           Source - https://www.sqlite.org/fileformat.html#b_tree_pages
        """

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.p = vlq_base128_be.VlqBase128Be(self._io)
            _on = 1 if self.p.value > self._root.header.index_x else 0
            if _on == 0:
                self.payload = Sqlite3.Record(self._io, self, self._root)
            elif _on == 1:
                self.payload = Sqlite3.OverflowRecord(
                    self.p.value, self._root.header.index_x, self._io, self, self._root
                )

    class IndexInteriorCell(KaitaiStruct):
        """
        .. seealso::
           Source - https://www.sqlite.org/fileformat.html#b_tree_pages
        """

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.left_child_page = Sqlite3.BtreePagePointer(self._io, self, self._root)
            self.p = vlq_base128_be.VlqBase128Be(self._io)
            _on = 1 if self.p.value > self._root.header.index_x else 0
            if _on == 0:
                self.payload = Sqlite3.Record(self._io, self, self._root)
            elif _on == 1:
                self.payload = Sqlite3.OverflowRecord(
                    self.p.value, self._root.header.index_x, self._io, self, self._root
                )

    class StringUtf8(KaitaiStruct):
        def __init__(self, length, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.length = length
            self._read()

        def _read(self):
            self.value = (self._io.read_bytes(self.length)).decode("UTF-8")

    class RecordHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.value_types = []
            i = 0
            while not self._io.is_eof():
                self.value_types.append(Sqlite3.SerialType(self._io, self, self._root))
                i += 1

    class StringUtf16Le(KaitaiStruct):
        def __init__(self, length, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.length = length
            self._read()

        def _read(self):
            self.value = (self._io.read_bytes(self.length)).decode("UTF-16LE")

    class TableInteriorCell(KaitaiStruct):
        """
        .. seealso::
           Source - https://www.sqlite.org/fileformat.html#b_tree_pages
        """

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.left_child_page = Sqlite3.BtreePagePointer(self._io, self, self._root)
            self.row_id = vlq_base128_be.VlqBase128Be(self._io)

    class DatabaseHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(16)
            if (
                not self.magic
                == b"\x53\x51\x4C\x69\x74\x65\x20\x66\x6F\x72\x6D\x61\x74\x20\x33\x00"
            ):
                raise kaitaistruct.ValidationNotEqualError(
                    b"\x53\x51\x4C\x69\x74\x65\x20\x66\x6F\x72\x6D\x61\x74\x20\x33\x00",
                    self.magic,
                    self._io,
                    "/types/database_header/seq/0",
                )
            self.page_size_raw = self._io.read_u2be()
            self.write_version = KaitaiStream.resolve_enum(
                Sqlite3.FormatVersion, self._io.read_u1()
            )
            self.read_version = KaitaiStream.resolve_enum(
                Sqlite3.FormatVersion, self._io.read_u1()
            )
            self.reserved_space = self._io.read_u1()
            self.max_payload_fraction = self._io.read_u1()
            self.min_payload_fraction = self._io.read_u1()
            self.leaf_payload_fraction = self._io.read_u1()
            self.file_change_counter = self._io.read_u4be()
            self.page_count = self._io.read_u4be()
            self.first_freelist_trunk_page = Sqlite3.FreelistTrunkPagePointer(
                self._io, self, self._root
            )
            self.freelist_page_count = self._io.read_u4be()
            self.schema_cookie = self._io.read_u4be()
            self.schema_format = self._io.read_u4be()
            self.def_page_cache_size = self._io.read_u4be()
            self.largest_root_page = self._io.read_u4be()
            self.text_encoding = self._io.read_u4be()
            self.user_version = self._io.read_u4be()
            self.is_incremental_vacuum = self._io.read_u4be()
            self.application_id = self._io.read_u4be()
            self.reserved = self._io.read_bytes(20)
            self.version_valid_for = self._io.read_u4be()
            self.sqlite_version_number = self._io.read_u4be()

        @property
        def table_x(self):
            """The maximum amount of inline table b-tree cell payload."""
            if hasattr(self, "_m_table_x"):
                return self._m_table_x

            self._m_table_x = self.usable_size - 35
            return getattr(self, "_m_table_x", None)

        @property
        def j(self):
            """The number of ptrmap entries per ptrmap page."""
            if hasattr(self, "_m_j"):
                return self._m_j

            self._m_j = self.usable_size // 5
            return getattr(self, "_m_j", None)

        @property
        def page_size(self):
            """The database page size in bytes."""
            if hasattr(self, "_m_page_size"):
                return self._m_page_size

            self._m_page_size = 65536 if self.page_size_raw == 1 else self.page_size_raw
            return getattr(self, "_m_page_size", None)

        @property
        def first_ptrmap_page_index(self):
            """The index (0-based) of the first ptrmap page."""
            if hasattr(self, "_m_first_ptrmap_page_index"):
                return self._m_first_ptrmap_page_index

            self._m_first_ptrmap_page_index = 1 if self.largest_root_page > 0 else 0
            return getattr(self, "_m_first_ptrmap_page_index", None)

        @property
        def m(self):
            """The minimum amount of inline b-tree cell payload."""
            if hasattr(self, "_m_m"):
                return self._m_m

            self._m_m = ((self.usable_size - 12) * 32) // 255 - 23
            return getattr(self, "_m_m", None)

        @property
        def last_ptrmap_page_index(self):
            """The index (0-based) of the last ptrmap page (inclusive)."""
            if hasattr(self, "_m_last_ptrmap_page_index"):
                return self._m_last_ptrmap_page_index

            self._m_last_ptrmap_page_index = (
                self.first_ptrmap_page_index + self.ptrmap_page_count
            ) - (
                0
                if (self.first_ptrmap_page_index + self.ptrmap_page_count)
                >= self.lock_byte_page_index
                else 1
            )
            return getattr(self, "_m_last_ptrmap_page_index", None)

        @property
        def index_x(self):
            """The maximum amount of inline index b-tree cell payload."""
            if hasattr(self, "_m_index_x"):
                return self._m_index_x

            self._m_index_x = ((self.usable_size - 12) * 64) // 255 - 23
            return getattr(self, "_m_index_x", None)

        @property
        def lock_byte_page_index(self):
            if hasattr(self, "_m_lock_byte_page_index"):
                return self._m_lock_byte_page_index

            self._m_lock_byte_page_index = 1073741824 // self.page_size
            return getattr(self, "_m_lock_byte_page_index", None)

        @property
        def ptrmap_page_count(self):
            """The number of ptrmap pages in the database."""
            if hasattr(self, "_m_ptrmap_page_count"):
                return self._m_ptrmap_page_count

            self._m_ptrmap_page_count = (
                (self.page_count // self.j + 1)
                if self.first_ptrmap_page_index > 0
                else 0
            )
            return getattr(self, "_m_ptrmap_page_count", None)

        @property
        def usable_size(self):
            """The "usable size" of a database page."""
            if hasattr(self, "_m_usable_size"):
                return self._m_usable_size

            self._m_usable_size = self.page_size - self.reserved_space
            return getattr(self, "_m_usable_size", None)

    class TableLeafCell(KaitaiStruct):
        """
        .. seealso::
           Source - https://www.sqlite.org/fileformat.html#b_tree_pages
        """

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.p = vlq_base128_be.VlqBase128Be(self._io)
            self.row_id = vlq_base128_be.VlqBase128Be(self._io)
            _on = 1 if self.p.value > self._root.header.table_x else 0
            if _on == 0:
                self.payload = Sqlite3.Record(self._io, self, self._root)
            elif _on == 1:
                self.payload = Sqlite3.OverflowRecord(
                    self.p.value, self._root.header.table_x, self._io, self, self._root
                )

    class CellPointer(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.content_offset = self._io.read_u2be()

        @property
        def content(self):
            if hasattr(self, "_m_content"):
                return self._m_content

            _pos = self._io.pos()
            self._io.seek(self.content_offset)
            _on = self._parent.page_type
            if _on == Sqlite3.BtreePageType.table_leaf:
                self._m_content = Sqlite3.TableLeafCell(self._io, self, self._root)
            elif _on == Sqlite3.BtreePageType.table_interior:
                self._m_content = Sqlite3.TableInteriorCell(self._io, self, self._root)
            elif _on == Sqlite3.BtreePageType.index_leaf:
                self._m_content = Sqlite3.IndexLeafCell(self._io, self, self._root)
            elif _on == Sqlite3.BtreePageType.index_interior:
                self._m_content = Sqlite3.IndexInteriorCell(self._io, self, self._root)
            self._io.seek(_pos)
            return getattr(self, "_m_content", None)

    class Value(KaitaiStruct):
        def __init__(self, serial_type, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.serial_type = serial_type
            self._read()

        def _read(self):
            _on = self.serial_type.value_type
            if _on == 14:
                self.value = Sqlite3.StringUtf16Le(
                    self.serial_type.content_size, self._io, self, self._root
                )
            elif _on == 0:
                self.value = Sqlite3.NullValue(self._io, self, self._root)
            elif _on == 4:
                self.value = self._io.read_s4be()
            elif _on == 6:
                self.value = self._io.read_s8be()
            elif _on == 7:
                self.value = self._io.read_f8be()
            elif _on == 1:
                self.value = self._io.read_s1()
            elif _on == 13:
                self.value = Sqlite3.StringUtf8(
                    self.serial_type.content_size, self._io, self, self._root
                )
            elif _on == 12:
                self.value = Sqlite3.Blob(
                    self.serial_type.content_size, self._io, self, self._root
                )
            elif _on == 3:
                self.value = self._io.read_bits_int_be(24)
            elif _on == 5:
                self.value = self._io.read_bits_int_be(48)
            elif _on == 15:
                self.value = Sqlite3.StringUtf16Be(
                    self.serial_type.content_size, self._io, self, self._root
                )
            elif _on == 8:
                self.value = Sqlite3.Int0(self._io, self, self._root)
            elif _on == 9:
                self.value = Sqlite3.Int1(self._io, self, self._root)
            elif _on == 2:
                self.value = self._io.read_s2be()

    class Blob(KaitaiStruct):
        def __init__(self, length, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.length = length
            self._read()

        def _read(self):
            self.value = self._io.read_bytes(self.length)

    class Record(KaitaiStruct):
        """
        .. seealso::
           Source - https://sqlite.org/fileformat2.html#record_format
        """

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header_length = vlq_base128_be.VlqBase128Be(self._io)
            self._raw_header = self._io.read_bytes((self.header_length.value - 1))
            _io__raw_header = KaitaiStream(BytesIO(self._raw_header))
            self.header = Sqlite3.RecordHeader(_io__raw_header, self, self._root)
            self.values = []
            for i in range(len(self.header.value_types)):
                self.values.append(
                    Sqlite3.Value(
                        self.header.value_types[i], self._io, self, self._root
                    )
                )

    @property
    def pages(self):
        if hasattr(self, "_m_pages"):
            return self._m_pages

        _pos = self._io.pos()
        self._io.seek(0)
        self._raw__m_pages = []
        self._m_pages = []
        for i in range(self.header.page_count):
            _on = (
                0
                if i == self.header.lock_byte_page_index
                else (
                    1
                    if (
                        (i >= self.header.first_ptrmap_page_index)
                        and (i <= self.header.last_ptrmap_page_index)
                    )
                    else 2
                )
            )
            if _on == 0:
                self._raw__m_pages.append(self._io.read_bytes(self.header.page_size))
                _io__raw__m_pages = KaitaiStream(BytesIO(self._raw__m_pages[i]))
                self._m_pages.append(
                    Sqlite3.LockBytePage((i + 1), _io__raw__m_pages, self, self._root)
                )
            elif _on == 1:
                self._raw__m_pages.append(self._io.read_bytes(self.header.page_size))
                _io__raw__m_pages = KaitaiStream(BytesIO(self._raw__m_pages[i]))
                self._m_pages.append(
                    Sqlite3.PtrmapPage((i + 1), _io__raw__m_pages, self, self._root)
                )
            elif _on == 2:
                self._raw__m_pages.append(self._io.read_bytes(self.header.page_size))
                _io__raw__m_pages = KaitaiStream(BytesIO(self._raw__m_pages[i]))
                self._m_pages.append(
                    Sqlite3.BtreePage((i + 1), _io__raw__m_pages, self, self._root)
                )
            else:
                self._m_pages.append(self._io.read_bytes(self.header.page_size))

        self._io.seek(_pos)
        return getattr(self, "_m_pages", None)
