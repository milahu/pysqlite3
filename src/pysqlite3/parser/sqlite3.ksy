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

  Each page would be of some type, and generally, they would be
  reached via the links starting from the first page. First page type
  (`root_page`) is always "btree_page".
doc-ref: https://www.sqlite.org/fileformat.html
seq:
  - id: header
    type: database_header
instances:
  pages:
    type:
      switch-on: '(_index == header.lock_byte_page_index ? 0 : _index >= header.first_ptrmap_page_index and _index <= header.last_ptrmap_page_index ? 1 : 2)'
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
    repeat-expr: header.page_count
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
      - id: reserved_space
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
      - id: page_count
        type: u4
        doc: Size of the database file in pages. The "in-header database size".
      - id: first_freelist_trunk_page
        type: freelist_trunk_page_pointer
        doc: Page number of the first freelist trunk page.
      - id: freelist_page_count
        type: u4
        doc: Total number of freelist pages.
      - id: schema_cookie
        type: u4
      - id: schema_format
        type: u4
        doc: The schema format number. Supported schema formats are 1, 2, 3, and 4.
      - id: def_page_cache_size
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
      - id: reserved
        size: 20
      - id: version_valid_for
        type: u4
      - id: sqlite_version_number
        type: u4
    instances:
      page_size:
        value: 'page_size_raw == 1 ? 0x10000 : page_size_raw'
        doc: The database page size in bytes
      usable_size:
        value: 'page_size - reserved_space'
        doc: The "usable size" of a database page
      m:
        value: ((usable_size-12)*32/255)-23
        doc: The minimum amount of inline b-tree cell payload
      table_x:
        value: usable_size - 35
        doc: The maximum amount of inline table b-tree cell payload
      index_x:
        value: ((usable_size-12)*64/255)-23
        doc: The maximum amount of inline index b-tree cell payload
      lock_byte_page_index:
        value: '1073741824 / page_size'
      j:
        value: usable_size/5
        doc: The number of ptrmap entries per ptrmap page
      first_ptrmap_page_index:
        value: 'largest_root_page > 0 ? 1 : 0'
        doc: The index (0-based) of the first ptrmap page
      ptrmap_page_count:
        value: 'first_ptrmap_page_index > 0 ? (page_count / j) + 1 : 0'
        doc: The number of ptrmap pages in the database
      last_ptrmap_page_index:
        value: 'first_ptrmap_page_index + ptrmap_page_count - (first_ptrmap_page_index + ptrmap_page_count >= lock_byte_page_index ? 0 : 1)'
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
        repeat-expr: entry_count
    instances:
      first_page:
        value: '3 + (_root.header.j * (page_number - 2))'
      last_page:
        value: 'first_page + _root.header.j - 1'
      entry_count:
        value: '(last_page > _root.header.page_count ? _root.header.page_count : last_page) - first_page + 1'
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
  btree_page:
    params:
      - id: page_number
        type: u4
    seq:
      - id: database_header
        type: database_header
        if: page_number == 1
      - id: page_type
        type: u1
        enum: btree_page_type
      - id: first_freeblock
        type: u2
        doc: The start of the first freeblock on the page, or is zero if there are no freeblocks.
      - id: cell_count
        type: u2
        doc: The number of cells on the page
      - id: cell_content_area_start_raw
        type: u2
        doc: |
          The start of the cell content area. A zero value for this integer is interpreted as 65536.
          The interpreted value is available as `cell_content_area`.
      - id: num_frag_free_bytes
        type: u1
        doc: The number of fragmented free bytes within the cell content area.
      - id: right_ptr
        type: btree_page_pointer
        if: page_type == btree_page_type::index_interior or page_type == btree_page_type::table_interior
        doc: |
          The right-most pointer. This value appears in the header of interior
          b-tree pages only and is omitted from all other pages.
      - id: cells
        type: cell_pointer
        repeat: expr
        repeat-expr: cell_count
    instances:
      call_content_area_start:
        value: 'cell_content_area_start_raw == 0 ? 65536 : cell_content_area_start_raw'
      cell_content_area:
        pos: call_content_area_start
        size: _root.header.usable_size - call_content_area_start
      reserved_area:
        pos: _root.header.page_size - _root.header.reserved_space
        size-eos: true
        if: _root.header.reserved_space != 0
  cell_pointer:
    seq:
      - id: content_offset
        type: u2
    instances:
      content:
        pos: content_offset
        type:
          switch-on: _parent.page_type
          cases:
            btree_page_type::table_leaf: table_leaf_cell
            btree_page_type::table_interior: table_interior_cell
            btree_page_type::index_leaf: index_leaf_cell
            btree_page_type::index_interior: index_interior_cell
  table_leaf_cell:
    doc-ref: 'https://www.sqlite.org/fileformat.html#b_tree_pages'
    seq:
      - id: p
        type: vlq_base128_be
      - id: row_id
        type: vlq_base128_be
      - id: payload
        type:
          switch-on: '(p.value > _root.header.table_x ? 1 : 0)'
          cases:
            0: record
            1: overflow_record(p.value, _root.header.table_x)
  table_interior_cell:
    doc-ref: 'https://www.sqlite.org/fileformat.html#b_tree_pages'
    seq:
      - id: left_child_page
        type: btree_page_pointer
      - id: row_id
        type: vlq_base128_be
  index_leaf_cell:
    doc-ref: 'https://www.sqlite.org/fileformat.html#b_tree_pages'
    seq:
      - id: p
        type: vlq_base128_be
      - id: payload
        type:
          switch-on: '(p.value > _root.header.index_x ? 1 : 0)'
          cases:
            0: record
            1: overflow_record(p.value, _root.header.index_x)
  index_interior_cell:
    doc-ref: 'https://www.sqlite.org/fileformat.html#b_tree_pages'
    seq:
      - id: left_child_page
        type: btree_page_pointer
      - id: p
        type: vlq_base128_be
      - id: payload
        type:
          switch-on: '(p.value > _root.header.index_x ? 1 : 0)'
          cases:
            0: record
            1: overflow_record(p.value, _root.header.index_x)
  record:
    doc-ref: 'https://sqlite.org/fileformat2.html#record_format'
    seq:
      - id: header_length
        type: vlq_base128_be
      - id: header
        type: record_header
        size: header_length.value - 1
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
    -webide-representation: "{value_type:dec}"
    seq:
      - id: code
        type: vlq_base128_be
    instances:
      value_type:
        value: 'code.value >= 12 ? ((code.value % 2 == 0) ? 12 : 13 + _root.header.text_encoding - 1) : code.value'
      content_size:
        value: (code.value - 12) / 2
        if: code.value >= 12
  value:
    params:
      - id: serial_type
        type: serial_type
    seq:
      - id: value
        type:
          switch-on: serial_type.value_type
          cases:
            0: null_value
            1: s1
            2: s2
            3: b24
            4: s4
            5: b48
            6: s8
            7: f8
            8: int_0
            9: int_1
            12: blob(serial_type.content_size)
            13: string_utf8(serial_type.content_size)
            14: string_utf16_le(serial_type.content_size)
            15: string_utf16_be(serial_type.content_size)
  null_value:
    -webide-representation: "NULL"
    seq: []
  int_0:
    -webide-representation: "0"
    seq: []
  int_1:
    -webide-representation: "1"
    seq: []
  string_utf8:
    params:
      - id: length
        type: u4
    seq:
      - id: value
        size: length
        type: str
        encoding: UTF-8
  string_utf16_be:
    params:
      - id: length
        type: u4
    seq:
      - id: value
        size: length
        type: str
        encoding: UTF-16BE
  string_utf16_le:
    params:
      - id: length
        type: u4
    seq:
      - id: value
        size: length
        type: str
        encoding: UTF-16LE
  blob:
    params:
      - id: length
        type: u4
    seq:
      - id: value
        size: length
  overflow_record:
    params:
      - id: payload_size
        type: u8
      - id: x
        type: u8
    seq:
      - id: inline_payload
        size: '(k <= x ? k : _root.header.m)'
      - id: overflow_page_number
        type: overflow_page_pointer
    instances:
      k:
        value: _root.header.m+((payload_size-_root.header.m)%(_root.header.usable_size-4))
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
      - id: l
        type: u4
      - id: free_pages
        type: u4
        repeat: expr
        repeat-expr: l
enums:
  format_version:
    1: legacy
    2: wal
  btree_page_type:
    0x02: index_interior
    0x05: table_interior
    0x0a: index_leaf
    0x0d: table_leaf
  ptrmap_page_type:
    1: root_page
    2: free_page
    3: overflow1
    4: overflow2
    5: btree
