meta:
  id: sqlite3
  title: SQLite3 database file
  file-extension:
    - sqlite
    - db
    - db3
    - sqlite3
  xref:
    forensicswiki: SQLite_database_format
    justsolve: SQLite
    loc: fdd000461
    pronom: fmt/729
    wikidata: Q28600453
  license: CC0-1.0
  imports:
    # A variable-length integer or "varint"
    # is a static Huffman encoding
    # of 64-bit twos-complement integers
    # that uses less space for small positive values.
    # A varint is between 1 and 9 bytes [128 bit] in length.
    # The varint consists of either zero or more bytes
    # which have the high-order bit set
    # followed by a single byte with the high-order bit clear,
    # or nine bytes, whichever is shorter.
    # The lower seven bits of each of the first eight bytes
    # and all 8 bits of the ninth byte
    # are used to reconstruct the 64-bit twos-complement integer.
    # Varints are big-endian:
    # bits taken from the earlier byte of the varint
    # are more significant than bits taken from the later bytes.
    - /common/vlq_base128_be
  endian: be
doc: |
  SQLite3 is a popular serverless SQL engine, implemented as a library
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
doc-ref: https://www.sqlite.org/fileformat2.html
seq:
  - id: header
    type: database_header
  - id: unused_page
    type: page(-1, -1)
    if: false
    doc: |
      unused type. useful for manually parsing pages.

      ```py
      import parser.sqlite3 as parser_sqlite3
      page = parser_sqlite3.Sqlite3.Page((i + 1), db._io, db, db._root)
      ```
instances:
  pages:
    type:
      switch-on: '(_index == header.idx_lock_byte_page ? 0 : _index >= header.idx_first_ptrmap_page and _index <= header.idx_last_ptrmap_page ? 1 : 2)'
      cases:
        0: lock_byte_page(_index + 1)
        1: ptrmap_page(_index + 1)
        # TODO: Free pages and cell overflow pages are incorrectly interpreted as btree pages
        # This is unfortunate, but unavoidable since there's no way to recognize these types at
        # this point in the parser.
        2: btree_page(_index + 1)
    pos: 0
    size: header.page_size
    repeat: expr
    repeat-expr: header.num_pages
    doc: |
      This works well when parsing small database files.

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
types:
  database_header:
    seq:
      - id: magic
        contents: ["SQLite format 3", 0]
      - id: page_size_raw
        type: u2
        doc: |
          The database page size in bytes. Must be a power of two between
          512 and 32768 inclusive, or the value 1 representing a page size
          of 65536. The interpreted value is available as `page_size`.
      - id: write_version
        type: u1
        enum: format_version
        doc: File format write version
      - id: read_version
        type: u1
        enum: format_version
        doc: File format read version
      - id: page_reserved_space_size
        type: u1
        doc: Bytes of unused "reserved" space at the end of each page. Usually 0.
      - id: max_payload_fraction
        type: u1
        doc: Maximum embedded payload fraction. Must be 64.
      - id: min_payload_fraction
        type: u1
        doc: Minimum embedded payload fraction. Must be 32.
      - id: leaf_payload_fraction
        type: u1
        doc: Leaf payload fraction. Must be 32.
      - id: file_change_counter
        type: u4
      - id: num_pages
        type: u4
        doc: Size of the database file in pages. The "in-header database size".
      - id: first_freelist_trunk_page
        type: freelist_trunk_page_pointer
        doc: Page number of the first freelist trunk page.
      - id: num_freelist_pages
        type: u4
        doc: Total number of freelist pages.
      - id: schema_cookie
        type: u4
      - id: schema_format
        type: u4
        doc: The schema format number. Supported schema formats are 1, 2, 3, and 4.
      - id: default_page_cache_size
        type: u4
        doc: Default page cache size.
      - id: largest_root_page
        type: u4
        doc: The page number of the largest root b-tree page when in auto-vacuum or incremental-vacuum modes, or zero otherwise.
      - id: text_encoding
        type: u4
        doc: The database text encoding. A value of 1 means UTF-8. A value of 2 means UTF-16le. A value of 3 means UTF-16be.
      - id: user_version
        type: u4
        doc: The "user version" as read and set by the user_version pragma.
      - id: is_incremental_vacuum
        type: u4
        doc: True (non-zero) for incremental-vacuum mode. False (zero) otherwise.
      - id: application_id
        type: u4
        doc: The "Application ID" set by PRAGMA application_id.
      - id: reserved_header_bytes
        size: 20
      - id: version_valid_for
        type: u4
      - id: sqlite_version_number
        type: u4
    instances:
      page_size:
        value: 'page_size_raw == 1 ? 65536 : page_size_raw'
        doc: The database page size in bytes
      usable_size:
        value: 'page_size - page_reserved_space_size'
        doc: The "usable size" of a database page
      overflow_min_payload_size:
        value: ((usable_size-12)*32/255)-23
        doc: The minimum amount of payload that must be stored on the btree page before spilling is allowed
      table_max_overflow_payload_size:
        value: usable_size - 35
        doc: The maximum amount of payload that can be stored directly on the b-tree page without spilling onto an overflow page. Value for table page
      index_max_overflow_payload_size:
        value: ((usable_size-12)*64/255)-23
        doc: The maximum amount of payload that can be stored directly on the b-tree page without spilling onto an overflow page. Value for index page
      idx_lock_byte_page:
        value: '1073741824 / page_size'
      num_ptrmap_entries_max:
        value: usable_size/5
        doc: The maximum number of ptrmap entries per ptrmap page
      idx_first_ptrmap_page:
        value: 'largest_root_page > 0 ? 1 : 0'
        doc: The index (0-based) of the first ptrmap page
      num_ptrmap_pages:
        value: 'idx_first_ptrmap_page > 0 ? (num_pages / num_ptrmap_entries_max) + 1 : 0'
        doc: The number of ptrmap pages in the database
      idx_last_ptrmap_page:
        value: 'idx_first_ptrmap_page + num_ptrmap_pages - (idx_first_ptrmap_page + num_ptrmap_pages >= idx_lock_byte_page ? 0 : 1)'
        doc: The index (0-based) of the last ptrmap page (inclusive)
  lock_byte_page:
    params:
      - id: page_number
        type: u4
    seq: []
    doc: |
      The lock-byte page is the single page of the database file that contains the bytes at offsets between
      1073741824 and 1073742335, inclusive. A database file that is less than or equal to 1073741824 bytes
      in size contains no lock-byte page. A database file larger than 1073741824 contains exactly one
      lock-byte page.
      The lock-byte page is set aside for use by the operating-system specific VFS implementation in implementing
      the database file locking primitives. SQLite does not use the lock-byte page.
  ptrmap_page:
    params:
      - id: page_number
        type: u4
    seq:
      - id: entries
        type: ptrmap_entry
        repeat: expr
        repeat-expr: num_entries
    instances:
      first_page:
        value: '3 + (_root.header.num_ptrmap_entries_max * (page_number - 2))'
      last_page:
        value: 'first_page + _root.header.num_ptrmap_entries_max - 1'
      num_entries:
        value: '(last_page > _root.header.num_pages ? _root.header.num_pages : last_page) - first_page + 1'
  ptrmap_entry:
    seq:
      - id: type
        type: u1
        enum: ptrmap_page_type
      - id: page_number
        type: u4
  btree_page_pointer:
    seq:
      - id: page_number
        type: u4
    instances:
      page:
        io: _root._io
        pos: (page_number - 1) * _root.header.page_size
        size: _root.header.page_size
        type: btree_page(page_number)
        if: page_number != 0
    doc: four-byte page number
  btree_page:
    params:
      - id: page_number
        type: u4
    seq:
      - id: database_header
        type: database_header
        if: page_number == 1
      # B-tree Page Header
      # 8 bytes for leaf pages
      # 12 bytes for interior pages
      - id: page_type
        type: u1
        enum: btree_page_type
      - id: first_freeblock
        type: u2
        doc: The start of the first freeblock on the page, or is zero if there are no freeblocks.
      - id: num_cell_pointers
        type: u2
        doc: The number of cells on the page
      - id: ofs_cell_content_area_raw
        type: u2
        doc: |
          The start of the cell content area. A zero value for this integer is interpreted as 65536.
          The interpreted value is available as `cell_content_area`.

          If the database uses a 65536-byte page size
          (page_size_raw == 1)
          and the reserved space is zero
          (the usual value for reserved space)
          then the cell content offset of an empty page
          wants to be 65536.
          However, that integer is too large to be stored
          in a 2-byte unsigned integer,
          so a value of 0 is used in its place.
      - id: num_frag_free_bytes
        type: u1
        doc: The number of fragmented free bytes within the cell content area.
      # only for interior pages:
      - id: rightmost_page_pointer
        type: btree_page_pointer
        if: |
          page_type == btree_page_type::index_interior_page or
          page_type == btree_page_type::table_interior_page
        doc: |
          The right-most pointer. This value appears in the header of interior
          b-tree pages only and is omitted from all other pages.
      # B-tree Page Body
      - id: cell_pointers
        type: cell_pointer
        repeat: expr
        repeat-expr: num_cell_pointers
        doc: |
          The cell pointers are arranged in key order
          with left-most cell (the cell with the smallest key) first
          and the right-most cell (the cell with the largest key) last.
    instances:
      ofs_cell_content_area:
        value: 'ofs_cell_content_area_raw == 0 ? 65536 : ofs_cell_content_area_raw'
      cell_content_area:
        pos: ofs_cell_content_area
        size: _root.header.usable_size - ofs_cell_content_area
      reserved_space:
        pos: _root.header.page_size - _root.header.page_reserved_space_size
        size-eos: true
        if: _root.header.page_reserved_space_size != 0
    doc: |
      Two variants of b-trees are used by SQLite:
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
  cell_pointer:
    seq:
      - id: ofs_content
        type: u2
    instances:
      content:
        #pos: ofs_content # wrong!
        # ofs_content is relative to page
        pos: ((_parent.page_number - 1) * _root.header.page_size) + ofs_content
        type:
          switch-on: _parent.page_type
          cases:
            btree_page_type::table_leaf_page: table_leaf_cell
            btree_page_type::table_interior_page: table_interior_cell
            btree_page_type::index_leaf_page: index_leaf_cell
            btree_page_type::index_interior_page: index_interior_cell
        doc: |
          Cell content is stored in the cell content region of the b-tree page.
  page:
    params:
      - id: page_number
        type: s4
      - id: ofs_body
        type: s4
    instances:
      page_index:
        value: 'page_number - 1'
      body:
        pos: ofs_body
        size: _root.header.page_size
        type:
          switch-on: |
            (
              page_index == _root.header.idx_lock_byte_page ? 0 :
              (
                _root.header.idx_first_ptrmap_page <= page_index
                and
                page_index <= _root.header.idx_last_ptrmap_page
              ) ? 1 :
              2
            )
          cases:
            0: lock_byte_page(page_number)
            1: ptrmap_page(page_number)
            # TODO: Free pages and cell overflow pages are incorrectly interpreted as btree pages
            # This is unfortunate, but unavoidable since there's no way to recognize these types at
            # this point in the parser.
            2: btree_page(page_number)
  table_leaf_cell:
    doc-ref: 'https://www.sqlite.org/fileformat2.html#b_tree_pages'
    seq:
      - id: payload_size
        type: vlq_base128_be
        doc: |
          total number of bytes of payload,
          including any overflow
      - id: row_id
        type: vlq_base128_be
        doc: |
          integer key, a.k.a. "rowid"
      # if all payload fits on the b-tree page:
      #   payload
      # else:
      #   payload + first_overflow_page_number
      - id: payload
        type:
          switch-on: |
            payload_size.value <= _root.header.table_max_overflow_payload_size
              ? 0
              : 1
          cases:
            0: record
            1: overflow_record(payload_size.value)
        doc: |
          The initial portion of the payload
          that does not spill to overflow pages.

          Payload, either table b-tree data or index b-tree keys,
          is always in the "record format".
          The record format defines a sequence of values
          corresponding to columns in a table or index.
          The record format specifies
          the number of columns,
          the datatype of each column, and
          the content of each column.

          sqlite/src/btreeInt.h:
          The key and data for any entry are combined to form the "payload".
          A fixed amount of payload can be carried directly on the database page.
          If the payload is larger than the preset amount
          then surplus bytes are stored on overflow pages.
          The payload for an entry and the preceding pointer
          are combined to form a "Cell".
          Each page has a small header which contains the Ptr(N) pointer
          and other information such as the size of key and data.
        doc-ref: https://www.sqlite.org/fileformat2.html#record_format
  table_interior_cell:
    doc-ref: 'https://www.sqlite.org/fileformat2.html#b_tree_pages'
    seq:
      # TODO rename to left_page_pointer?
      - id: left_child_page_pointer
        type: btree_page_pointer
      - id: row_id
        type: vlq_base128_be
  index_leaf_cell:
    doc-ref: 'https://www.sqlite.org/fileformat2.html#b_tree_pages'
    seq:
      - id: payload_size
        type: vlq_base128_be
      - id: payload
        type:
          switch-on: '(payload_size.value > _root.header.index_max_overflow_payload_size ? 1 : 0)'
          cases:
            0: record
            1: overflow_record(payload_size.value)
  index_interior_cell:
    doc-ref: 'https://www.sqlite.org/fileformat2.html#b_tree_pages'
    seq:
      - id: left_child_page_pointer
        type: btree_page_pointer
      - id: payload_size
        type: vlq_base128_be
      - id: payload
        type:
          switch-on: '(payload_size.value > _root.header.index_max_overflow_payload_size ? 1 : 0)'
          cases:
            0: record
            1: overflow_record(payload_size.value)
  record:
    doc-ref: 'https://sqlite.org/fileformat2.html#record_format'
    seq:
      - id: header_size
        type: vlq_base128_be
      - id: header
        type: record_header
        size: header_size.value - 1
      - id: values
        type: value(header.value_types[_index])
        repeat: expr
        repeat-expr: header.value_types.size
  record_header:
    seq:
      - id: value_types
        type: serial_type
        repeat: eos
  serial_type:
    -webide-representation: "{type:dec}"
    seq:
      - id: raw_value
        type: vlq_base128_be
    instances:
      type:
        # NOTE(string_encoding): Workaround for string encoding:
        # 13 + _root.header.text_encoding - 1
        # See type serial:
        # 12: blob
        # 13: string_utf8
        # 14: string_utf16_le
        # 15: string_utf16_be
        value: 'raw_value.value >= 12 ? ((raw_value.value % 2 == 0) ? 12 : 13 + _root.header.text_encoding - 1) : raw_value.value'
        enum: serial
      len_blob_string:
        value: '(raw_value.value % 2 == 0) ? (raw_value.value - 12) / 2 : (raw_value.value - 13) / 2'
        if: raw_value.value >= 12
        doc: |
          sizes of other types:

          ```py
          size_of_type = [0, 1, 2, 3, 4, 6, 8, 8, 0, 0]
          # size_of_type[10]: variable size of internal_1
          # size_of_type[11]: variable size of internal_2
          ```
  value:
    params:
      - id: serial_type
        type: serial_type
    seq:
      - id: value
        type:
          switch-on: serial_type.type
          cases:
            serial::null: null_value
            serial::int8: s1
            serial::int16: s2
            serial::int24: b24
            serial::int32: s4
            serial::int48: b48
            serial::int64: s8
            serial::float64: f8
            serial::number_0: int_0
            serial::number_1: int_1
            serial::blob: blob(serial_type.len_blob_string)
            # NOTE(string_encoding): Workaround for string encoding:
            serial::string_utf8: string_utf8(serial_type.len_blob_string)
            serial::string_utf16_le: string_utf16_le(serial_type.len_blob_string)
            serial::string_utf16_be: string_utf16_be(serial_type.len_blob_string)
    doc: |
      in records, type and value are stored separately:
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

  value_at_offset:
    params:
      - id: serial_type
        type: serial_type
      - id: value_offset
        type: u4 # TODO larger? page_number is u4, page_size_raw is u2
    seq:
      - id: value
        type:
          switch-on: serial_type.type
          cases:
            serial::null: null_value
            serial::int8: s1
            serial::int16: s2
            serial::int24: b24
            serial::int32: s4
            serial::int48: b48
            serial::int64: s8
            serial::float64: f8
            serial::number_0: int_0
            serial::number_1: int_1
            serial::blob: blob(serial_type.len_blob_string)
            # NOTE(string_encoding): Workaround for string encoding:
            serial::string_utf8: string_utf8(serial_type.len_blob_string)
            serial::string_utf16_le: string_utf16_le(serial_type.len_blob_string)
            serial::string_utf16_be: string_utf16_be(serial_type.len_blob_string)
  null_value:
    -webide-representation: "NULL"
    seq: []
    # limitation: kaitai-struct has no explicit null value
    #instances:
    #  value:
    #    value: "null" # error: unable to access 'null' in sqlite3::null_value context
    #    value: null # error: expected string, got null
    #    value: NULL # error: expected string, got null
    #    value: # error: expected string, got null
    #    value: "NULL" # error: invalid ID: 'NULL', expected /^[a-z][a-z0-9_]*$/
  int_0:
    #-webide-representation: "0"
    seq: []
    instances:
      value:
        value: 0
  int_1:
    #-webide-representation: "1"
    seq: []
    instances:
      value:
        value: 1
  string_utf8:
    params:
      - id: len_value
        type: u4
    seq:
      - id: value
        size: len_value
        type: str
        encoding: UTF-8
  string_utf16_be:
    params:
      - id: len_value
        type: u4
    seq:
      - id: value
        size: len_value
        type: str
        encoding: UTF-16BE
  string_utf16_le:
    params:
      - id: len_value
        type: u4
    seq:
      - id: value
        size: len_value
        type: str
        encoding: UTF-16LE
  blob:
    params:
      - id: len_value
        type: u4
    seq:
      - id: value
        size: len_value
  overflow_record:
    params:
      - id: payload_size
        type: u8
    seq:
      - id: inline_payload
        size: |
          inline_payload_size <= _root.header.table_max_overflow_payload_size
            ? inline_payload_size
            : _root.header.overflow_min_payload_size
        doc: |
          A record contains a header and a body, in that order.

          The header begins with a single varint
          which determines the total number of bytes in the header.
          The varint value is the size of the header in bytes
          including the size varint itself.

          Following the size varint are one or more additional varints, one per column.
          These additional varints are called "serial type" numbers
          and determine the datatype of each column.

          Overflow records must be parsed manually,
          because the record (header and body)
          can be fragmented across multiple pages.

          ```py
          # TODO add sample code
          ```

          When a record spans across multiple pages,
          then the record data is right-aligned:
          Only the first page is **not** fully used,
          and all following pages are fully used.

          The first page stores
          `inline_payload_size` bytes.

          All following pages store
          `(_root.header.usable_size - 4)` bytes.
      - id: first_overflow_page_number
        type: overflow_page_pointer
        doc: |
          page number for the first page
          of the overflow page list
    instances:
      inline_payload_size:
        value: |
          _root.header.overflow_min_payload_size + (
            (payload_size - _root.header.overflow_min_payload_size) %
            (_root.header.usable_size - 4)
          )
  overflow_page_pointer:
    seq:
      - id: page_number
        type: u4
    instances:
      page:
        io: _root._io
        pos: (page_number - 1) * _root.header.page_size
        size: _root.header.page_size
        type: overflow_page
        if: page_number != 0
        doc: |
          NOTE(memleak): if you use this interface on a large database,
          all pages will be cached, and the process can run out of memory.
          instead: get the page_number, and manually read and parse the page:

          ```py
          page_number = some_page_pointer.page_number
          page_index = page_number - 1
          page_offset = page_index * con._db.header.page_size
          page = Sqlite3.Page(page_number, page_offset, db._io, db, db._root)
          ```
  overflow_page:
    seq:
      - id: next_page_number
        type: overflow_page_pointer
      - id: content
        size: _root.header.page_size - 4
  freelist_trunk_page_pointer:
    seq:
      - id: page_number
        type: u4
    instances:
      page:
        io: _root._io
        pos: (page_number - 1) * _root.header.page_size
        size: _root.header.page_size
        type: freelist_trunk_page
        if: page_number != 0
  freelist_trunk_page:
    seq:
      - id: next_page
        type: freelist_trunk_page_pointer
      - id: num_free_pages
        type: u4
      - id: free_pages
        type: u4
        repeat: expr
        repeat-expr: num_free_pages
enums:
  format_version:
    1: legacy
    2: wal
  btree_page_type:
    0x02: index_interior_page
    0x05: table_interior_page
    0x0a: index_leaf_page
    0x0d: table_leaf_page
  ptrmap_page_type:
    1: root_page
    2: free_page
    3: overflow1
    4: overflow2
    5: btree
  serial:
    # Value is NULL.
    # This can mean that the value is stored in row_id.
    0: "null"
    # Values are twos-complement integers from 8 to 64 bit.
    1: int8
    2: int16
    3: int24
    4: int32
    5: int48
    6: int64
    # Value is a big-endian IEEE 754-2008 64-bit floating point number.
    7: float64
    # Value is the integer 0 or 1. (Only available for schema format 4 and higher.)
    8: number_0
    9: number_1
    # Reserved for internal use. These serial type codes will never appear in a
    # well-formed database file, but they might be used in transient and temporary
    # database files that SQLite sometimes generates for its own use. The meanings
    # of these codes can shift from one release of SQLite to the next.
    10: internal_1
    11: internal_2
    # The serial types for blob and string are 'N >= 12 and even' and 'N >=13 and odd' respectively
    # The enum here differs slightly to have a single value for blob and a value per text encoding
    # for string.
    #
    # Value is a BLOB that is (N-12)/2 bytes in length.
    12: blob
    # Value is a string in the text encoding and (N-13)/2 bytes in length. The nul terminator is
    # not stored.
    # NOTE(string_encoding): Workaround for string encoding:
    # Originally, sqlite3 has only one string type,
    # and the string encoding is stored in _root.header.text_encoding.
    13: string_utf8
    14: string_utf16_le
    15: string_utf16_be
