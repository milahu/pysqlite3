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

    Each page would be of some type (btree, ptrmap, lock_byte, or free),
    and generally, they would be reached via the links starting from the
    first page. The first page is always a btree page for the implicitly
    defined `sqlite_schema` table.

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

    class Serial(Enum):
        nil = 0
        two_comp_8 = 1
        two_comp_16 = 2
        two_comp_24 = 3
        two_comp_32 = 4
        two_comp_48 = 5
        two_comp_64 = 6
        ieee754_64 = 7
        integer_0 = 8
        integer_1 = 9
        internal_1 = 10
        internal_2 = 11
        blob = 12
        string_utf8 = 13
        string_utf16_le = 14
        string_utf16_be = 15

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
            self.num_cells = self._io.read_u2be()
            self.ofs_cell_content_area_raw = self._io.read_u2be()
            self.num_frag_free_bytes = self._io.read_u1()
            if (self.page_type == Sqlite3.BtreePageType.index_interior) or (
                self.page_type == Sqlite3.BtreePageType.table_interior
            ):
                self.right_ptr = Sqlite3.BtreePagePointer(self._io, self, self._root)

            self.cells = []
            for i in range(self.num_cells):
                self.cells.append(Sqlite3.CellPointer(self._io, self, self._root))

        @property
        def ofs_cell_content_area(self):
            if hasattr(self, "_m_ofs_cell_content_area"):
                return self._m_ofs_cell_content_area

            self._m_ofs_cell_content_area = (
                65536
                if self.ofs_cell_content_area_raw == 0
                else self.ofs_cell_content_area_raw
            )
            return getattr(self, "_m_ofs_cell_content_area", None)

        @property
        def cell_content_area(self):
            if hasattr(self, "_m_cell_content_area"):
                return self._m_cell_content_area

            _pos = self._io.pos()
            self._io.seek(self.ofs_cell_content_area)
            self._m_cell_content_area = self._io.read_bytes(
                (self._root.header.usable_size - self.ofs_cell_content_area)
            )
            self._io.seek(_pos)
            return getattr(self, "_m_cell_content_area", None)

        @property
        def reserved_space(self):
            if hasattr(self, "_m_reserved_space"):
                return self._m_reserved_space

            if self._root.header.page_reserved_space_size != 0:
                _pos = self._io.pos()
                self._io.seek(
                    (
                        self._root.header.page_size
                        - self._root.header.page_reserved_space_size
                    )
                )
                self._m_reserved_space = self._io.read_bytes_full()
                self._io.seek(_pos)

            return getattr(self, "_m_reserved_space", None)

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
        def __init__(
            self, payload_size, overflow_payload_size_max, _io, _parent=None, _root=None
        ):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.payload_size = payload_size
            self.overflow_payload_size_max = overflow_payload_size_max
            self._read()

        def _read(self):
            self.inline_payload = self._io.read_bytes(
                (
                    self.inline_payload_size
                    if self.inline_payload_size <= self.overflow_payload_size_max
                    else self._root.header.overflow_min_payload_size
                )
            )
            self.overflow_page_number = Sqlite3.OverflowPagePointer(
                self._io, self, self._root
            )

        @property
        def inline_payload_size(self):
            if hasattr(self, "_m_inline_payload_size"):
                return self._m_inline_payload_size

            self._m_inline_payload_size = (
                self._root.header.overflow_min_payload_size
                + (
                    (self.payload_size - self._root.header.overflow_min_payload_size)
                    % (self._root.header.usable_size - 4)
                )
            )
            return getattr(self, "_m_inline_payload_size", None)

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
            self.num_free_pages = self._io.read_u4be()
            self.free_pages = []
            for i in range(self.num_free_pages):
                self.free_pages.append(self._io.read_u4be())

    class Page(KaitaiStruct):
        def __init__(self, page_number, ofs_body, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.page_number = page_number
            self.ofs_body = ofs_body
            self._read()

        def _read(self):
            pass

        @property
        def page_index(self):
            if hasattr(self, "_m_page_index"):
                return self._m_page_index

            self._m_page_index = self.page_number - 1
            return getattr(self, "_m_page_index", None)

        @property
        def body(self):
            if hasattr(self, "_m_body"):
                return self._m_body

            _pos = self._io.pos()
            self._io.seek(self.ofs_body)
            _on = (
                0
                if self.page_index == self._root.header.idx_lock_byte_page
                else (
                    1
                    if (
                        (self.page_index >= self._root.header.idx_first_ptrmap_page)
                        and (self.page_index <= self._root.header.idx_last_ptrmap_page)
                    )
                    else 2
                )
            )
            if _on == 0:
                self._raw__m_body = self._io.read_bytes(self._root.header.page_size)
                _io__raw__m_body = KaitaiStream(BytesIO(self._raw__m_body))
                self._m_body = Sqlite3.LockBytePage(
                    self.page_number, _io__raw__m_body, self, self._root
                )
            elif _on == 1:
                self._raw__m_body = self._io.read_bytes(self._root.header.page_size)
                _io__raw__m_body = KaitaiStream(BytesIO(self._raw__m_body))
                self._m_body = Sqlite3.PtrmapPage(
                    self.page_number, _io__raw__m_body, self, self._root
                )
            elif _on == 2:
                self._raw__m_body = self._io.read_bytes(self._root.header.page_size)
                _io__raw__m_body = KaitaiStream(BytesIO(self._raw__m_body))
                self._m_body = Sqlite3.BtreePage(
                    self.page_number, _io__raw__m_body, self, self._root
                )
            else:
                self._m_body = self._io.read_bytes(self._root.header.page_size)
            self._io.seek(_pos)
            return getattr(self, "_m_body", None)

    class PtrmapPage(KaitaiStruct):
        def __init__(self, page_number, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.page_number = page_number
            self._read()

        def _read(self):
            self.entries = []
            for i in range(self.num_entries):
                self.entries.append(Sqlite3.PtrmapEntry(self._io, self, self._root))

        @property
        def first_page(self):
            if hasattr(self, "_m_first_page"):
                return self._m_first_page

            self._m_first_page = 3 + (
                self._root.header.num_ptrmap_entries_max * (self.page_number - 2)
            )
            return getattr(self, "_m_first_page", None)

        @property
        def last_page(self):
            if hasattr(self, "_m_last_page"):
                return self._m_last_page

            self._m_last_page = (
                self.first_page + self._root.header.num_ptrmap_entries_max
            ) - 1
            return getattr(self, "_m_last_page", None)

        @property
        def num_entries(self):
            if hasattr(self, "_m_num_entries"):
                return self._m_num_entries

            self._m_num_entries = (
                (
                    self._root.header.num_pages
                    if self.last_page > self._root.header.num_pages
                    else self.last_page
                )
                - self.first_page
            ) + 1
            return getattr(self, "_m_num_entries", None)

    class StringUtf16Be(KaitaiStruct):
        def __init__(self, len_value, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.len_value = len_value
            self._read()

        def _read(self):
            self.value = (self._io.read_bytes(self.len_value)).decode("UTF-16BE")

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
            self.raw_value = vlq_base128_be.VlqBase128Be(self._io)

        @property
        def type(self):
            if hasattr(self, "_m_type"):
                return self._m_type

            self._m_type = KaitaiStream.resolve_enum(
                Sqlite3.Serial,
                (
                    (
                        12
                        if (self.raw_value.value % 2) == 0
                        else ((13 + self._root.header.text_encoding) - 1)
                    )
                    if self.raw_value.value >= 12
                    else self.raw_value.value
                ),
            )
            return getattr(self, "_m_type", None)

        @property
        def variable_size(self):
            if hasattr(self, "_m_variable_size"):
                return self._m_variable_size

            if self.raw_value.value >= 12:
                self._m_variable_size = (self.raw_value.value - 12) // 2

            return getattr(self, "_m_variable_size", None)

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
            self.payload_size = vlq_base128_be.VlqBase128Be(self._io)
            _on = (
                1
                if self.payload_size.value
                > self._root.header.index_max_overflow_payload_size
                else 0
            )
            if _on == 0:
                self.payload = Sqlite3.Record(self._io, self, self._root)
            elif _on == 1:
                self.payload = Sqlite3.OverflowRecord(
                    self.payload_size.value,
                    self._root.header.index_max_overflow_payload_size,
                    self._io,
                    self,
                    self._root,
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
            self.payload_size = vlq_base128_be.VlqBase128Be(self._io)
            _on = (
                1
                if self.payload_size.value
                > self._root.header.index_max_overflow_payload_size
                else 0
            )
            if _on == 0:
                self.payload = Sqlite3.Record(self._io, self, self._root)
            elif _on == 1:
                self.payload = Sqlite3.OverflowRecord(
                    self.payload_size.value,
                    self._root.header.index_max_overflow_payload_size,
                    self._io,
                    self,
                    self._root,
                )

    class StringUtf8(KaitaiStruct):
        def __init__(self, len_value, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.len_value = len_value
            self._read()

        def _read(self):
            self.value = (self._io.read_bytes(self.len_value)).decode("UTF-8")

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
        def __init__(self, len_value, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.len_value = len_value
            self._read()

        def _read(self):
            self.value = (self._io.read_bytes(self.len_value)).decode("UTF-16LE")

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
            self.page_reserved_space_size = self._io.read_u1()
            self.max_payload_fraction = self._io.read_u1()
            self.min_payload_fraction = self._io.read_u1()
            self.leaf_payload_fraction = self._io.read_u1()
            self.file_change_counter = self._io.read_u4be()
            self.num_pages = self._io.read_u4be()
            self.first_freelist_trunk_page = Sqlite3.FreelistTrunkPagePointer(
                self._io, self, self._root
            )
            self.num_freelist_pages = self._io.read_u4be()
            self.schema_cookie = self._io.read_u4be()
            self.schema_format = self._io.read_u4be()
            self.def_page_cache_size = self._io.read_u4be()
            self.largest_root_page = self._io.read_u4be()
            self.text_encoding = self._io.read_u4be()
            self.user_version = self._io.read_u4be()
            self.is_incremental_vacuum = self._io.read_u4be()
            self.application_id = self._io.read_u4be()
            self.reserved_header_bytes = self._io.read_bytes(20)
            self.version_valid_for = self._io.read_u4be()
            self.sqlite_version_number = self._io.read_u4be()

        @property
        def num_ptrmap_pages(self):
            """The number of ptrmap pages in the database."""
            if hasattr(self, "_m_num_ptrmap_pages"):
                return self._m_num_ptrmap_pages

            self._m_num_ptrmap_pages = (
                (self.num_pages // self.num_ptrmap_entries_max + 1)
                if self.idx_first_ptrmap_page > 0
                else 0
            )
            return getattr(self, "_m_num_ptrmap_pages", None)

        @property
        def idx_last_ptrmap_page(self):
            """The index (0-based) of the last ptrmap page (inclusive)."""
            if hasattr(self, "_m_idx_last_ptrmap_page"):
                return self._m_idx_last_ptrmap_page

            self._m_idx_last_ptrmap_page = (
                self.idx_first_ptrmap_page + self.num_ptrmap_pages
            ) - (
                0
                if (self.idx_first_ptrmap_page + self.num_ptrmap_pages)
                >= self.idx_lock_byte_page
                else 1
            )
            return getattr(self, "_m_idx_last_ptrmap_page", None)

        @property
        def idx_first_ptrmap_page(self):
            """The index (0-based) of the first ptrmap page."""
            if hasattr(self, "_m_idx_first_ptrmap_page"):
                return self._m_idx_first_ptrmap_page

            self._m_idx_first_ptrmap_page = 1 if self.largest_root_page > 0 else 0
            return getattr(self, "_m_idx_first_ptrmap_page", None)

        @property
        def overflow_min_payload_size(self):
            """The minimum amount of payload that must be stored on the btree page before spilling is allowed."""
            if hasattr(self, "_m_overflow_min_payload_size"):
                return self._m_overflow_min_payload_size

            self._m_overflow_min_payload_size = (
                (self.usable_size - 12) * 32
            ) // 255 - 23
            return getattr(self, "_m_overflow_min_payload_size", None)

        @property
        def num_ptrmap_entries_max(self):
            """The maximum number of ptrmap entries per ptrmap page."""
            if hasattr(self, "_m_num_ptrmap_entries_max"):
                return self._m_num_ptrmap_entries_max

            self._m_num_ptrmap_entries_max = self.usable_size // 5
            return getattr(self, "_m_num_ptrmap_entries_max", None)

        @property
        def idx_lock_byte_page(self):
            if hasattr(self, "_m_idx_lock_byte_page"):
                return self._m_idx_lock_byte_page

            self._m_idx_lock_byte_page = 1073741824 // self.page_size
            return getattr(self, "_m_idx_lock_byte_page", None)

        @property
        def page_size(self):
            """The database page size in bytes."""
            if hasattr(self, "_m_page_size"):
                return self._m_page_size

            self._m_page_size = 65536 if self.page_size_raw == 1 else self.page_size_raw
            return getattr(self, "_m_page_size", None)

        @property
        def table_max_overflow_payload_size(self):
            """The maximum amount of payload that can be stored directly on the b-tree page without spilling onto an overflow page. Value for table page."""
            if hasattr(self, "_m_table_max_overflow_payload_size"):
                return self._m_table_max_overflow_payload_size

            self._m_table_max_overflow_payload_size = self.usable_size - 35
            return getattr(self, "_m_table_max_overflow_payload_size", None)

        @property
        def index_max_overflow_payload_size(self):
            """The maximum amount of payload that can be stored directly on the b-tree page without spilling onto an overflow page. Value for index page."""
            if hasattr(self, "_m_index_max_overflow_payload_size"):
                return self._m_index_max_overflow_payload_size

            self._m_index_max_overflow_payload_size = (
                (self.usable_size - 12) * 64
            ) // 255 - 23
            return getattr(self, "_m_index_max_overflow_payload_size", None)

        @property
        def usable_size(self):
            """The "usable size" of a database page."""
            if hasattr(self, "_m_usable_size"):
                return self._m_usable_size

            self._m_usable_size = self.page_size - self.page_reserved_space_size
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
            self.payload_size = vlq_base128_be.VlqBase128Be(self._io)
            self.row_id = vlq_base128_be.VlqBase128Be(self._io)
            _on = (
                1
                if self.payload_size.value
                > self._root.header.table_max_overflow_payload_size
                else 0
            )
            if _on == 0:
                self.payload = Sqlite3.Record(self._io, self, self._root)
            elif _on == 1:
                self.payload = Sqlite3.OverflowRecord(
                    self.payload_size.value,
                    self._root.header.table_max_overflow_payload_size,
                    self._io,
                    self,
                    self._root,
                )

    class CellPointer(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_content = self._io.read_u2be()

        @property
        def content(self):
            if hasattr(self, "_m_content"):
                return self._m_content

            _pos = self._io.pos()
            self._io.seek(self.ofs_content)
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
            _on = self.serial_type.type
            if _on == Sqlite3.Serial.integer_0:
                self.value = Sqlite3.Int0(self._io, self, self._root)
            elif _on == Sqlite3.Serial.two_comp_24:
                self.value = self._io.read_bits_int_be(24)
            elif _on == Sqlite3.Serial.nil:
                self.value = Sqlite3.NullValue(self._io, self, self._root)
            elif _on == Sqlite3.Serial.blob:
                self.value = Sqlite3.Blob(
                    self.serial_type.variable_size, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.string_utf8:
                self.value = Sqlite3.StringUtf8(
                    self.serial_type.variable_size, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.two_comp_16:
                self.value = self._io.read_s2be()
            elif _on == Sqlite3.Serial.ieee754_64:
                self.value = self._io.read_f8be()
            elif _on == Sqlite3.Serial.two_comp_8:
                self.value = self._io.read_s1()
            elif _on == Sqlite3.Serial.string_utf16_be:
                self.value = Sqlite3.StringUtf16Be(
                    self.serial_type.variable_size, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.two_comp_48:
                self.value = self._io.read_bits_int_be(48)
            elif _on == Sqlite3.Serial.integer_1:
                self.value = Sqlite3.Int1(self._io, self, self._root)
            elif _on == Sqlite3.Serial.string_utf16_le:
                self.value = Sqlite3.StringUtf16Le(
                    self.serial_type.variable_size, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.two_comp_32:
                self.value = self._io.read_s4be()
            elif _on == Sqlite3.Serial.two_comp_64:
                self.value = self._io.read_s8be()

    class Blob(KaitaiStruct):
        def __init__(self, len_value, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.len_value = len_value
            self._read()

        def _read(self):
            self.value = self._io.read_bytes(self.len_value)

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
            self.header_size = vlq_base128_be.VlqBase128Be(self._io)
            self._raw_header = self._io.read_bytes((self.header_size.value - 1))
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

        class PagesList:
            def __init__(self, root):
                self.root = root

            def __len__(self):
                return self.root.header.num_pages

            def __getitem__(self, i):  # i is 0-based
                if i < 0:  # -1 means last page, etc
                    i = self.root.header.num_pages + i

                assert (
                    0 <= i and i < self.root.header.num_pages
                ), f"page index is out of range: {i} is not in (0, {self.root.header.num_pages - 1})"

                # TODO LRU cache with sparse array?
                # note: LRU cache does not give pointer equality
                # but equality check is trivial: page_a.page_number == page_b.page_number

                _pos = self.root._io.pos()
                self.root._io.seek(i * self.root.header.page_size)
                page = Sqlite3.Page(
                    (i + 1), (self.root.header.page_size * i), self.root._io, self.root, self.root._root
                )
                self.root._io.seek(_pos)
                return page

        self._m_pages = PagesList(self)
        return getattr(self, "_m_pages", None)

    @property
    def root_pages(self):
        if hasattr(self, "_m_root_pages"):
            return self._m_root_pages

        _pos = self._io.pos()
        self._raw__m_root_pages = []
        self._m_root_pages = []
        i = 0
        i_max = self.header.num_pages - 1
        while i < i_max:  # `i == i_max` means "end of file"
            self._io.seek(i * self.header.page_size)
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
            assert _on == 2
            self._m_root_pages.append(
                Sqlite3.BtreePage((i + 1), self._io, self, self._root)
            )

            page = self._m_root_pages[-1]

            # FIXME page.right_ptr should be None by default
            # `if page.right_ptr:` is faster than `if hasattr(page, "right_ptr"):`
            # generally, struct layout should be constant = all fields are always present
            # because this allows for memory optimization

            # go to next root page
            if hasattr(page, "right_ptr"):
                i = page.right_ptr.page_number - 1
            else:
                i = i + 1

        self._io.seek(_pos)
        return getattr(self, "_m_root_pages", None)
