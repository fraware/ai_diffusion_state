"""Streaming parser for MySQL-style IIDS SQL dumps (INSERT / CREATE TABLE)."""
from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CHUNK_BYTES = 8 * 1024 * 1024

_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+`?(?P<table>[A-Za-z0-9_]+)`?\s*\(",
    re.IGNORECASE,
)
_INSERT_RE = re.compile(
    r"INSERT\s+INTO\s+`?(?P<table>[A-Za-z0-9_]+)`?"
    r"(?:\s*\((?P<columns>[^)]+)\))?\s*VALUES\s*(?P<values>.+)",
    re.IGNORECASE | re.DOTALL,
)
_COLUMN_NAME_RE = re.compile(r"`([^`]+)`|([A-Za-z_][A-Za-z0-9_]*)")


@dataclass(frozen=True)
class SqlInsertBatch:
    table: str
    columns: tuple[str, ...] | None
    rows: tuple[tuple[object, ...], ...]


def _unescape_sql_string(raw: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch != "\\" or i + 1 >= len(raw):
            out.append(ch)
            i += 1
            continue
        nxt = raw[i + 1]
        mapping = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", "'": "'", '"': '"', "0": "\0"}
        out.append(mapping.get(nxt, nxt))
        i += 2
    return "".join(out)


def parse_sql_value(token: str) -> object:
    token = token.strip()
    if not token or token.upper() == "NULL":
        return None
    if token.startswith("'") and token.endswith("'"):
        return _unescape_sql_string(token[1:-1])
    if token.startswith('"') and token.endswith('"'):
        return _unescape_sql_string(token[1:-1])
    try:
        if "." in token:
            return float(token)
        return int(token)
    except ValueError:
        return token


def split_sql_tuple_values(tuple_body: str) -> list[object]:
    values: list[object] = []
    i = 0
    n = len(tuple_body)
    while i < n:
        while i < n and tuple_body[i] in " \t\r\n,":
            i += 1
        if i >= n:
            break
        start = i
        if tuple_body[i] == "'":
            i += 1
            while i < n:
                if tuple_body[i] == "\\" and i + 1 < n:
                    i += 2
                    continue
                if tuple_body[i] == "'":
                    i += 1
                    break
                i += 1
            values.append(parse_sql_value(tuple_body[start:i]))
            continue
        if tuple_body[i] == '"':
            i += 1
            while i < n:
                if tuple_body[i] == "\\" and i + 1 < n:
                    i += 2
                    continue
                if tuple_body[i] == '"':
                    i += 1
                    break
                i += 1
            values.append(parse_sql_value(tuple_body[start:i]))
            continue
        while i < n and tuple_body[i] not in ",":
            i += 1
        values.append(parse_sql_value(tuple_body[start:i]))
    return values


def split_sql_row_tuples(values_clause: str) -> list[str]:
    rows: list[str] = []
    depth = 0
    start = 0
    in_quote: str | None = None
    i = 0
    n = len(values_clause)
    while i < n:
        ch = values_clause[i]
        if in_quote:
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == in_quote:
                in_quote = None
            i += 1
            continue
        if ch in ("'", '"'):
            in_quote = ch
            i += 1
            continue
        if ch == "(":
            if depth == 0:
                start = i + 1
            depth += 1
            i += 1
            continue
        if ch == ")":
            depth -= 1
            if depth == 0:
                rows.append(values_clause[start:i])
            i += 1
            continue
        i += 1
    return rows


def parse_create_table_columns(ddl_block: str) -> list[str]:
    m = _CREATE_TABLE_RE.search(ddl_block)
    if not m:
        return []
    open_paren = ddl_block.find("(", m.end() - 1)
    if open_paren < 0:
        return []
    depth = 0
    end = -1
    for idx in range(open_paren, len(ddl_block)):
        if ddl_block[idx] == "(":
            depth += 1
        elif ddl_block[idx] == ")":
            depth -= 1
            if depth == 0:
                end = idx
                break
    if end < 0:
        return []
    body = ddl_block[open_paren + 1 : end]
    columns: list[str] = []
    for part in body.split(","):
        piece = part.strip()
        if not piece or piece.upper().startswith(("PRIMARY ", "KEY ", "UNIQUE ", "CONSTRAINT ", "INDEX ")):
            continue
        cm = re.match(r"`?([A-Za-z_][A-Za-z0-9_]*)`?", piece)
        if cm:
            columns.append(cm.group(1))
    return columns


def parse_insert_statement(statement: str) -> SqlInsertBatch | None:
    m = _INSERT_RE.match(statement.strip().rstrip(";"))
    if not m:
        return None
    table = m.group("table")
    columns_raw = m.group("columns")
    columns: tuple[str, ...] | None = None
    if columns_raw:
        cols = []
        for cm in _COLUMN_NAME_RE.finditer(columns_raw):
            cols.append(cm.group(1) or cm.group(2))
        columns = tuple(cols)
    values_clause = m.group("values").strip().rstrip(";")
    row_bodies = split_sql_row_tuples(values_clause)
    rows: list[tuple[object, ...]] = []
    for body in row_bodies:
        parsed = split_sql_tuple_values(body)
        if parsed:
            rows.append(tuple(parsed))
    if not rows:
        return None
    return SqlInsertBatch(table=table, columns=columns, rows=tuple(rows))


def _statement_buffer_iter(path: Path, chunk_bytes: int) -> Iterator[str]:
    buf = ""
    with path.open("r", encoding="utf-8", errors="replace") as f:
        while True:
            chunk = f.read(chunk_bytes)
            if not chunk:
                break
            buf += chunk
            while True:
                semi = buf.find(";")
                if semi < 0:
                    break
                stmt = buf[: semi + 1]
                buf = buf[semi + 1 :]
                stmt = stmt.strip()
                if stmt:
                    yield stmt
        tail = buf.strip()
        if tail:
            yield tail


def stream_table_inserts(
    path: Path,
    table_name: str,
    *,
    chunk_bytes: int = DEFAULT_CHUNK_BYTES,
    table_columns: dict[str, list[str]] | None = None,
) -> Iterator[dict[str, object]]:
    """Yield row dicts for INSERTs targeting ``table_name``."""
    table_columns = table_columns or {}
    default_cols = table_columns.get(table_name)
    for statement in _statement_buffer_iter(path, chunk_bytes):
        upper = statement.upper()
        if upper.startswith("CREATE TABLE"):
            cols = parse_create_table_columns(statement)
            if cols:
                table_columns[table_name] = cols
            continue
        if not upper.startswith("INSERT INTO"):
            continue
        batch = parse_insert_statement(statement)
        if batch is None or batch.table != table_name:
            continue
        columns = batch.columns or tuple(table_columns.get(table_name, ()))
        if not columns:
            continue
        for row in batch.rows:
            if len(row) != len(columns):
                continue
            yield dict(zip(columns, row, strict=False))
