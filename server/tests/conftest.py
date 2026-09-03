"""Transaction-rollback isolation for tests that exercise the live DB.

Week 20 d2. The integration tests here drive the real production tools
(append_claim, append_ruling, delete_claim), and those tools each open
their own connection via server.db.client.get_connection and commit
internally. Run as-written against SUPABASE_DB_URL they leave permanent
rows behind: eight fixture rulings and 48 "throwaway" claims had
accumulated in production before this fixture existed.

The fixture makes every get_connection() call within a test hand back one
shared connection whose commit() is a no-op, so the tools' internal
commits are absorbed and the whole test rolls back at teardown. Nothing
the tools do needs to change, and they stay exercised through their real
code paths rather than being mocked out.

Two details this depends on:

- close() is neutralized as well. The tools call conn.close() in their
  finally blocks; without this the first tool call would close the shared
  connection and every later call in the same test would fail.
- Autocommit stays off and the caller never commits, so the server holds
  one open transaction for the test's duration. Reads issued through the
  same connection see the uncommitted rows — which is what lets the
  production queries be asserted against normally.
"""

from __future__ import annotations

import importlib

import pytest
from psycopg2.extras import RealDictCursor

from server.db import client as db_client

# Modules that did `from server.db.client import get_connection` at import
# time hold their own binding, so patching db_client alone would not reach
# them. Each is rebound individually.
_MODULES_BINDING_GET_CONNECTION = (
    "server.tools.append_claim",
    "server.tools.append_ruling",
    "server.tools.delete_claim",
)

# get_claim_status and check_substantiation read through these helpers,
# which open their own connections; they are rebound to the shared one so
# reads see the test's uncommitted rows.
_MODULES_BINDING_FETCH_HELPERS = (
    "server.tools.get_claim_status",
    "server.tools.check_substantiation",
    "server.tools.classify_claim_risk",
    "server.tools.list_claims",
)


class _NoCommitConnection:
    """Proxy that absorbs commit() and close() on a shared connection.

    psycopg2's connection is a C extension type whose commit/close are
    read-only attributes, so they cannot be monkeypatched on the instance.
    The tools call both in their normal flow; this proxy swallows them and
    forwards everything else (cursor, rollback, encoding, …) unchanged.
    """

    def __init__(self, conn):
        self._conn = conn

    def commit(self):  # absorbed — the fixture owns transaction boundaries
        pass

    def close(self):  # absorbed — the fixture closes the real connection
        pass

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def __enter__(self):
        self._conn.__enter__()
        return self

    def __exit__(self, *exc):
        # psycopg2's context manager commits on clean exit; suppress that
        # so a `with conn:` block inside a tool cannot escape the rollback.
        return None


@pytest.fixture
def rollback_db(monkeypatch):
    """Route all DB access through one rolled-back transaction.

    Yields the proxied connection so a test can issue its own SQL on it and
    see the same uncommitted state the tools wrote.
    """
    real_conn = db_client.get_connection()
    real_conn.autocommit = False
    conn = _NoCommitConnection(real_conn)

    def _shared_connection():
        return conn

    def _fetchone_dict(query, params=()):
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None

    def _fetchall_dict(query, params=()):
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    def _execute(query, params=()):
        with conn.cursor() as cur:
            cur.execute(query, params)

    monkeypatch.setattr(db_client, "get_connection", _shared_connection)
    monkeypatch.setattr(db_client, "fetchone_dict", _fetchone_dict)
    monkeypatch.setattr(db_client, "fetchall_dict", _fetchall_dict)
    monkeypatch.setattr(db_client, "execute", _execute)

    for name in _MODULES_BINDING_GET_CONNECTION:
        mod = importlib.import_module(name)
        if hasattr(mod, "get_connection"):
            monkeypatch.setattr(mod, "get_connection", _shared_connection)

    for name in _MODULES_BINDING_FETCH_HELPERS:
        mod = importlib.import_module(name)
        if hasattr(mod, "fetchone_dict"):
            monkeypatch.setattr(mod, "fetchone_dict", _fetchone_dict)
        if hasattr(mod, "fetchall_dict"):
            monkeypatch.setattr(mod, "fetchall_dict", _fetchall_dict)
        if hasattr(mod, "execute"):
            monkeypatch.setattr(mod, "execute", _execute)

    try:
        yield conn
    finally:
        # Roll back and close through the real connection, never the proxy —
        # the proxy's close() is a no-op by design.
        try:
            real_conn.rollback()
        finally:
            real_conn.close()
