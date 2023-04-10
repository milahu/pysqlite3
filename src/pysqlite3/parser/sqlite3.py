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

    This works well when parsing small database files. To parse large
    database files, see the documentation for /instances/pages.

    Further documentation:

    - https://www.sqlite.org/arch.html
    - https://cstack.github.io/db_tutorial/parts/part7.html
    - https://en.wikipedia.org/wiki/B%2B-tree # B+-tree
    - https://en.wikipedia.org/wiki/B-tree

    Original sources:

    - https://github.com/sqlite/sqlite/blob/master/src/btreeInt.h
    - https://github.com/sqlite/sqlite/blob/master/src/btree.h
    - https://github.com/sqlite/sqlite/blob/master/src/btree.c

    .. seealso::
       Source - https://www.sqlite.org/fileformat2.html
    """

    class FormatVersion(Enum):
        legacy = 1
        wal = 2

    class BtreePageType(Enum):
        index_interior_page = 2
        table_interior_page = 5
        index_leaf_page = 10
        table_leaf_page = 13

    class PtrmapPageType(Enum):
        root_page = 1
        free_page = 2
        overflow1 = 3
        overflow2 = 4
        btree = 5

    class Serial(Enum):
        null = 0
        int8 = 1
        int16 = 2
        int24 = 3
        int32 = 4
        int48 = 5
        int64 = 6
        float64 = 7
        number_0 = 8
        number_1 = 9
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
        if False:
            self.unused_page = Sqlite3.Page(-1, -1, self._io, self, self._root)

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
        """Two variants of b-trees are used by SQLite:
        "Table b-trees" use a 64-bit signed integer key
        and store all data in the leaves.
        "Index b-trees" use arbitrary keys
        and store no data at all.

        A b-tree page is
        either an interior page or a leaf page:
        A leaf page contains keys
        and in the case of a table b-tree
        each key has associated data.
        An interior page contains K keys
        together with K+1 pointers to child b-tree pages.

        A "pointer" in an interior b-tree page
        is just the 32-bit unsigned integer
        page number of the child page.

        Large keys on index b-trees are
        split up into overflow pages
        so that no single key uses more than one fourth
        of the available storage space on the page
        and hence every internal page
        is able to store at least 4 keys.
        The integer keys of table b-trees
        are never large enough to require overflow,
        so key overflow only occurs on index b-trees.

        In an interior b-tree page,
        the pointers and keys logically alternate
        with a pointer on both ends.
        All keys within the same page are unique
        and are logically organized
        in ascending order from left to right.
        For any key X,
        pointers to the left of a X refer to b-tree pages
        on which all keys are less than or equal to X.
        Pointers to the right of X refer to pages
        where all keys are greater than X.

        Within an interior b-tree page,
        each key and the pointer to its immediate left
        are combined into a structure called a "cell".
        The right-most pointer is held separately.

        A leaf b-tree page has no pointers,
        but it still uses the cell structure
        to hold keys for index b-trees
        or keys and content for table b-trees.
        Data is also contained in the cell.

        interior page of table/index b-tree:
        cell = key + left_pointer

        leaf page of table b-tree:
        cell = keys + content

        leaf page of index b-tree:
        cell = keys

        The cell pointer array of a b-tree page
        immediately follows the b-tree page header.
        Let K be the number of cells on the btree.
        The cell pointer array consists of
        K 2-byte integer offsets to the cell contents.
        The cell pointers are arranged in key order.

        Cell content is stored
        in the cell content region of the b-tree page.

        If a page contains no cells
        (which is only possible for a root page of a table
        that contains no rows)
        then the offset to the cell content area will equal
        the page size minus the bytes of reserved space.
        """

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
            self.num_cell_pointers = self._io.read_u2be()
            self.ofs_cell_content_area_raw = self._io.read_u2be()
            self.num_frag_free_bytes = self._io.read_u1()
            if (self.page_type == Sqlite3.BtreePageType.index_interior_page) or (
                self.page_type == Sqlite3.BtreePageType.table_interior_page
            ):
                self.rightmost_page_pointer = Sqlite3.BtreePagePointer(
                    self._io, self, self._root
                )

            self.cell_pointers = []
            for i in range(self.num_cell_pointers):
                self.cell_pointers.append(
                    Sqlite3.CellPointer(self._io, self, self._root)
                )

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

    class ValueAtOffset(KaitaiStruct):
        def __init__(self, serial_type, value_offset, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.serial_type = serial_type
            self.value_offset = value_offset
            self._read()

        def _read(self):
            _on = self.serial_type.type
            if _on == Sqlite3.Serial.int16:
                self.value = self._io.read_s2be()
            elif _on == Sqlite3.Serial.int64:
                self.value = self._io.read_s8be()
            elif _on == Sqlite3.Serial.float64:
                self.value = self._io.read_f8be()
            elif _on == Sqlite3.Serial.int24:
                self.value = self._io.read_bits_int_be(24)
            elif _on == Sqlite3.Serial.blob:
                self.value = Sqlite3.Blob(
                    self.serial_type.len_blob_string, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.string_utf8:
                self.value = Sqlite3.StringUtf8(
                    self.serial_type.len_blob_string, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.null:
                self.value = Sqlite3.NullValue(self._io, self, self._root)
            elif _on == Sqlite3.Serial.number_0:
                self.value = Sqlite3.Int0(self._io, self, self._root)
            elif _on == Sqlite3.Serial.string_utf16_be:
                self.value = Sqlite3.StringUtf16Be(
                    self.serial_type.len_blob_string, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.int48:
                self.value = self._io.read_bits_int_be(48)
            elif _on == Sqlite3.Serial.int32:
                self.value = self._io.read_s4be()
            elif _on == Sqlite3.Serial.int8:
                self.value = self._io.read_s1()
            elif _on == Sqlite3.Serial.string_utf16_le:
                self.value = Sqlite3.StringUtf16Le(
                    self.serial_type.len_blob_string, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.number_1:
                self.value = Sqlite3.Int1(self._io, self, self._root)

    class BtreePagePointer(KaitaiStruct):
        """four-byte page number."""

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

        @property
        def value(self):
            if hasattr(self, "_m_value"):
                return self._m_value

            self._m_value = 0
            return getattr(self, "_m_value", None)

    class OverflowRecord(KaitaiStruct):
        def __init__(self, payload_size, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.payload_size = payload_size
            self._read()

        def _read(self):
            self.inline_payload = self._io.read_bytes(
                (
                    self.inline_payload_size
                    if self.inline_payload_size
                    <= self._root.header.table_max_overflow_payload_size
                    else self._root.header.overflow_min_payload_size
                )
            )
            self.first_overflow_page_number = Sqlite3.OverflowPagePointer(
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
                        (self._root.header.idx_first_ptrmap_page <= self.page_index)
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

        @property
        def value(self):
            if hasattr(self, "_m_value"):
                return self._m_value

            self._m_value = 1
            return getattr(self, "_m_value", None)

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
            """NOTE(memleak): if you use this interface on a large database,
            all pages will be cached, and the process can run out of memory.
            instead: get the page_number, and manually read and parse the page:

            ```py
            page_number = some_page_pointer.page_number
            page_index = page_number - 1
            page_offset = page_index * con._db.header.page_size
            page = Sqlite3.Page(page_number, page_offset, db._io, db, db._root)
            ```
            """
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
        def len_blob_string(self):
            """sizes of other types:

            ```py
            size_of_type = [0, 1, 2, 3, 4, 6, 8, 8, 0, 0]
            # size_of_type[10]: variable size of internal_1
            # size_of_type[11]: variable size of internal_2
            ```
            """
            if hasattr(self, "_m_len_blob_string"):
                return self._m_len_blob_string

            if self.raw_value.value >= 12:
                self._m_len_blob_string = (
                    (self.raw_value.value - 12) // 2
                    if (self.raw_value.value % 2) == 0
                    else (self.raw_value.value - 13) // 2
                )

            return getattr(self, "_m_len_blob_string", None)

    class IndexLeafCell(KaitaiStruct):
        """
        .. seealso::
           Source - https://www.sqlite.org/fileformat2.html#b_tree_pages
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
                    self.payload_size.value, self._io, self, self._root
                )

    class IndexInteriorCell(KaitaiStruct):
        """
        .. seealso::
           Source - https://www.sqlite.org/fileformat2.html#b_tree_pages
        """

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.left_child_page_pointer = Sqlite3.BtreePagePointer(
                self._io, self, self._root
            )
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
                    self.payload_size.value, self._io, self, self._root
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
           Source - https://www.sqlite.org/fileformat2.html#b_tree_pages
        """

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.left_child_page_pointer = Sqlite3.BtreePagePointer(
                self._io, self, self._root
            )
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
            self.default_page_cache_size = self._io.read_u4be()
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
           Source - https://www.sqlite.org/fileformat2.html#b_tree_pages
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
                0
                if self.payload_size.value
                <= self._root.header.table_max_overflow_payload_size
                else 1
            )
            if _on == 0:
                self.payload = Sqlite3.Record(self._io, self, self._root)
            elif _on == 1:
                self.payload = Sqlite3.OverflowRecord(
                    self.payload_size.value, self._io, self, self._root
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
            """Cell content is stored in the cell content region of the b-tree page."""
            if hasattr(self, "_m_content"):
                return self._m_content

            _pos = self._io.pos()
            self._io.seek(
                (
                    ((self._parent.page_number - 1) * self._root.header.page_size)
                    + self.ofs_content
                )
            )
            _on = self._parent.page_type
            if _on == Sqlite3.BtreePageType.table_leaf_page:
                self._m_content = Sqlite3.TableLeafCell(self._io, self, self._root)
            elif _on == Sqlite3.BtreePageType.table_interior_page:
                self._m_content = Sqlite3.TableInteriorCell(self._io, self, self._root)
            elif _on == Sqlite3.BtreePageType.index_leaf_page:
                self._m_content = Sqlite3.IndexLeafCell(self._io, self, self._root)
            elif _on == Sqlite3.BtreePageType.index_interior_page:
                self._m_content = Sqlite3.IndexInteriorCell(self._io, self, self._root)
            self._io.seek(_pos)
            return getattr(self, "_m_content", None)

    class Value(KaitaiStruct):
        """in records, type and value are stored separately:
        types are stored in the record header,
        values are stored in the record body.

        to parse a record value:

        ```py
        import parser.sqlite3 as parser_sqlite3
        # TODO: class PayloadReader
        payload_reader = PayloadReader(db, page, cell_pointer_idx)
        payload_io = parser_sqlite3.KaitaiStream(payload_reader)
        value = parser_sqlite3.Sqlite3.Value(value_type, payload_io, db, db._root)
        ```
        """

        def __init__(self, serial_type, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.serial_type = serial_type
            self._read()

        def _read(self):
            _on = self.serial_type.type
            if _on == Sqlite3.Serial.int16:
                self.value = self._io.read_s2be()
            elif _on == Sqlite3.Serial.int64:
                self.value = self._io.read_s8be()
            elif _on == Sqlite3.Serial.float64:
                self.value = self._io.read_f8be()
            elif _on == Sqlite3.Serial.int24:
                self.value = self._io.read_bits_int_be(24)
            elif _on == Sqlite3.Serial.blob:
                self.value = Sqlite3.Blob(
                    self.serial_type.len_blob_string, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.string_utf8:
                self.value = Sqlite3.StringUtf8(
                    self.serial_type.len_blob_string, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.null:
                self.value = Sqlite3.NullValue(self._io, self, self._root)
            elif _on == Sqlite3.Serial.number_0:
                self.value = Sqlite3.Int0(self._io, self, self._root)
            elif _on == Sqlite3.Serial.string_utf16_be:
                self.value = Sqlite3.StringUtf16Be(
                    self.serial_type.len_blob_string, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.int48:
                self.value = self._io.read_bits_int_be(48)
            elif _on == Sqlite3.Serial.int32:
                self.value = self._io.read_s4be()
            elif _on == Sqlite3.Serial.int8:
                self.value = self._io.read_s1()
            elif _on == Sqlite3.Serial.string_utf16_le:
                self.value = Sqlite3.StringUtf16Le(
                    self.serial_type.len_blob_string, self._io, self, self._root
                )
            elif _on == Sqlite3.Serial.number_1:
                self.value = Sqlite3.Int1(self._io, self, self._root)

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
        """This works well when parsing small database files.

        problem:
        the first access to db.pages
        for example `db.pages[0]`
        will loop and parse **all** pages.

        To parse large database files,
        the user should set
        the internal cache attribute `db._m_pages`
        so that any access to `db.pages`
        will use the cached value in `db._m_pages`.

        ```py
        # import sqlite3.py generated from sqlite3.ksy
        import parser.sqlite3 as parser_sqlite3
        # create a lazy list class
        # accessing db.pages[i] will call pages_list.__getitem__(i)
        class PagesList:
            def __init__(self, db):
                self.db = db
            def __len__(self):
                return self.db.header.num_pages
            def __getitem__(self, i):  # i is 0-based
                db = self.db
                header = db.header
                if i < 0:  # -1 means last page, etc
                    i = header.num_pages + i
                assert (
                    0 <= i and i < header.num_pages
                ), f"page index is out of range: {i} is not in (0, {header.num_pages - 1})"
                # todo: maybe cache page
                # equality test: page_a.page_number == page_b.page_number
                _pos = db._io.pos()
                db._io.seek(i * header.page_size)
                if i == header.idx_lock_byte_page:
                    page = parser_sqlite3.Sqlite3.LockBytePage((i + 1), db._io, db, db._root)
                elif (
                    i >= header.idx_first_ptrmap_page and
                    i <= header.idx_last_ptrmap_page
                ):
                    page = parser_sqlite3.Sqlite3.PtrmapPage((i + 1), db._io, db, db._root)
                else:
                    page = parser_sqlite3.Sqlite3.BtreePage((i + 1), db._io, db, db._root)
                db._io.seek(_pos)
                return page
        # create a database parser
        database = "test.db"
        db = parser_sqlite3.Sqlite3.from_file(database)
        # patch the internal cache attribute of db.pages
        db._m_pages = PagesList(db)
        # now, this will parse **only** the first page
        page = db.pages[0]
        ```
        """
        if hasattr(self, "_m_pages"):
            return self._m_pages

        _pos = self._io.pos()
        self._io.seek(0)
        self._raw__m_pages = []
        self._m_pages = []
        for i in range(self.header.num_pages):
            _on = (
                0
                if i == self.header.idx_lock_byte_page
                else (
                    1
                    if (
                        (i >= self.header.idx_first_ptrmap_page)
                        and (i <= self.header.idx_last_ptrmap_page)
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
