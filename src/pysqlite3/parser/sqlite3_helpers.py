from typing import List, Tuple

from . import sqlite3 as parser_sqlite3

class PagesList:
    """
    lazy list for db.pages

    avoid parsing all pages of a large database file
    """
    def __init__(self, db):
        self.db = db
        self._debug = False

    def __len__(self):
        return self.db.header.num_pages

    def __getitem__(self, page_idx):  # page_idx is 0-based
        """
        lazy getter for db.pages[page_idx]
        """
        if self._debug:
            print(f"PagesList.__getitem__({page_idx})")
        db = self.db
        header = db.header
        if page_idx < 0:  # -1 means last page, etc
            page_idx = header.num_pages + page_idx
        assert (
            0 <= page_idx and page_idx < header.num_pages
        ), f"page index is out of range: {page_idx} is not in (0, {header.num_pages - 1})"
        # todo: maybe cache page
        # equality test: page_a.page_number == page_b.page_number
        _pos = db._io.pos()
        db._io.seek(page_idx * header.page_size)
        if page_idx == header.idx_lock_byte_page:
            page = parser_sqlite3.Sqlite3.LockBytePage((page_idx + 1), db._io, db, db._root)
        elif (
            page_idx >= header.idx_first_ptrmap_page and
            page_idx <= header.idx_last_ptrmap_page
        ):
            page = parser_sqlite3.Sqlite3.PtrmapPage((page_idx + 1), db._io, db, db._root)
        else:
            page = parser_sqlite3.Sqlite3.BtreePage((page_idx + 1), db._io, db, db._root)
        db._io.seek(_pos)
        return page


class PayloadReader:
    """
    buffered reader to read payload from multiple pages
    """
    pos = 0
    _debug = False
    def __init__(self, db, first_page, cell_pointer_idx):
        self.db = db
        self.first_page = first_page
        self.cell_pointer_idx = cell_pointer_idx
        assert (
            isinstance(first_page, parser_sqlite3.Sqlite3.BtreePage) or
            # TODO more?
            False
        ), f"wrong type of first_page. expected BtreePage. actual {type(first_page)}"
        self.first_payload = first_page.cell_pointers[cell_pointer_idx].content.payload
    def read(self, size):
        # _last_read_positions: list of tuples: (page, start, size)
        # page is page_index (zero-based)
        # start is relative to page
        self._last_read_positions: List[Tuple(int, int, int)] = []
        start = self.pos
        end = start + size
        page_loop_idx = 0
        page_number = self.first_page.page_number
        page_index = page_number - 1
        cell_pointer_idx = self.cell_pointer_idx
        # TODO optimize. currently we loop chunks
        # and for every chunk we do a range-check.
        # instead, seek to the first chunk,
        # then loop all chunks in range
        # TODO buffer the last page across multiple read calls,
        # to continue reading from the last position
        # this is faster when reading multiple large values (blobs or strings)
        if end < len(self.first_payload.inline_payload):
            # simple case: all data is in the first page
            self.pos += size
            ofs_content = self.first_page.cell_pointers[cell_pointer_idx].ofs_content
            inline_payload_offset = ofs_content # TODO verify
            #raise NotImplementedError("inline_payload_offset")
            relative_start = inline_payload_offset + start
            absolute_start = page_index * self.db.header.page_size + 4 + relative_start # TODO verify +4. page header?
            chunk_size = size
            chunk_bytes = self.first_payload.inline_payload[start:end]
            buf = chunk_bytes
            size_remains = size - len(buf)
            if self._debug:
                print(f"PayloadReader: page_loop_idx={page_loop_idx}: buf += {chunk_bytes[0:16]}...")
                with open(dbfile, "rb") as f:
                    f.seek(absolute_start)
                    expected_bytes = f.read(chunk_size)
                    if expected_bytes != chunk_bytes:
                        print(f"PayloadReader: page_loop_idx={page_loop_idx}: chunk_bytes:    {chunk_bytes[0:16]}...")
                        print(f"PayloadReader: page_loop_idx={page_loop_idx}: expected_bytes: {expected_bytes[0:16]}...")
                    assert expected_bytes == chunk_bytes # TODO verify +4. page header?
            #relative_end = relative_start + size
            self._last_read_positions.append((page_index, relative_start, chunk_size))
            return buf
        # complex case: data is fragmented over multiple pages
        if self._debug:
            print()
            print(f"PayloadReader: start: {start}")
            print(f"PayloadReader: size: {size}")
        payload_chunk_start = 0
        next_payload_chunk_start = len(self.first_payload.inline_payload)
        if self._debug:
            print(f"PayloadReader: page_loop_idx={page_loop_idx}: page number: {page_number}")
            print(f"PayloadReader: page_loop_idx={page_loop_idx}: len(self.first_payload.inline_payload):", len(self.first_payload.inline_payload))
        if start < next_payload_chunk_start:
            # first chunk
            ofs_content = self.first_page.cell_pointers[cell_pointer_idx].ofs_content
            inline_payload_offset = ofs_content # TODO verify
            #raise NotImplementedError("inline_payload_offset")
            relative_start = inline_payload_offset + start
            absolute_start = page_index * self.db.header.page_size + 4 + relative_start # TODO verify +4. page header?
            chunk_bytes = self.first_payload.inline_payload[start:end]
            chunk_size = len(chunk_bytes)
            buf = chunk_bytes # first chunk
            if self._debug:
                print(f"PayloadReader: page_loop_idx={page_loop_idx}: buf += {chunk_bytes[0:16]}...")
                with open(dbfile, "rb") as f:
                    f.seek(absolute_start)
                    expected_bytes = f.read(chunk_size)
                    if expected_bytes != chunk_bytes:
                        print(f"PayloadReader: page_loop_idx={page_loop_idx}: chunk_bytes:    {chunk_bytes[0:16]}...")
                        print(f"PayloadReader: page_loop_idx={page_loop_idx}: expected_bytes: {expected_bytes[0:16]}...")
                    assert expected_bytes == chunk_bytes # TODO verify +4. page header?

            buf = self.first_payload.inline_payload[start:]
            end = start + len(buf)
            #self._last_read_positions.append((start, end))
            self._last_read_positions.append((page_index, relative_start, chunk_size))
            if self._debug:
                print(f"PayloadReader: page_loop_idx={page_loop_idx}: buf += {buf[0:16]}...")
            size_remains = size - len(buf) # not used?
        else:
            buf = b""
            size_remains = size
        page = self.first_payload.first_overflow_page_number.page
        page_number = self.first_payload.first_overflow_page_number.page_number
        page_index = page_number - 1
        while len(buf) < size:
            # first or next chunk
            page_loop_idx += 1
            payload_chunk_start = next_payload_chunk_start
            if self._debug:
                print(f"PayloadReader: page_loop_idx={page_loop_idx}: buf: {len(buf)} of {size}")
            assert page
            next_payload_chunk_start = payload_chunk_start + len(page.content)
            if start < next_payload_chunk_start:
                relative_start = max(0, start - payload_chunk_start)
                relative_end = min(len(page.content), relative_start + size_remains)
                if self._debug:
                    print()
                    print(f"PayloadReader: page_loop_idx={page_loop_idx}: page: {page}")
                    print(f"PayloadReader: page_loop_idx={page_loop_idx}: page number: {page_number}")
                    print(f"PayloadReader: page_loop_idx={page_loop_idx}: payload_chunk_start: {payload_chunk_start}")
                    #print(f"PayloadReader: page_loop_idx={page_loop_idx}: size_remains: {size_remains}")
                chunk_size = relative_end - relative_start
                if self._debug:
                    print(f"PayloadReader: page_loop_idx={page_loop_idx}: chunk_size: {chunk_size}")
                    print(f"PayloadReader: page_loop_idx={page_loop_idx}: relative_start: {relative_start}")
                    #print(f"PayloadReader: page_loop_idx={page_loop_idx}: relative_end: {relative_end}")
                #absolute_start = page_index * self.db.header.page_size + relative_start # wrong
                absolute_start = page_index * self.db.header.page_size + 4 + relative_start # TODO verify +4. page header?
                if self._debug:
                    print(f"PayloadReader: page_loop_idx={page_loop_idx}: absolute_start: {absolute_start}")
                    #print(f"PayloadReader: page_loop_idx={page_loop_idx}: absolute_end: {relative_end}")
                self._last_read_positions.append((page_index, relative_start, chunk_size))
                chunk_bytes = page.content[relative_start:relative_end]
                buf += chunk_bytes
                size_remains = size - len(buf)
                if self._debug:
                    print(f"PayloadReader: page_loop_idx={page_loop_idx}: buf += {chunk_bytes[0:16]}...")
                    with open(dbfile, "rb") as f:
                        f.seek(absolute_start)
                        expected_bytes = f.read(chunk_size)
                        if expected_bytes != chunk_bytes:
                            print(f"PayloadReader: page_loop_idx={page_loop_idx}: chunk_bytes:    {chunk_bytes[0:16]}...")
                            print(f"PayloadReader: page_loop_idx={page_loop_idx}: expected_bytes: {expected_bytes[0:16]}...")
                        assert expected_bytes == chunk_bytes # TODO verify +4. page header?
            page_number = page.next_page_number.page_number
            page_index = page_number - 1
            page = page.next_page_number.page
        assert len(buf) == size
        self.pos += size
        return buf
    def seek(self, pos):
        self.pos = pos

