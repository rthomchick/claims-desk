"""
Database connection for the Claims Desk registry. Connects to Supabase
(PostgreSQL) via psycopg2, always through the pooler (port 6543) —
the direct connection (port 5432) fails with IPv6 routing on Supabase,
same failure mode documented in the SAFe Feature Spec System's ADR-003.
"""

from __future__ import annotations

import os
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor, Json

from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Return a psycopg2 connection using the Supabase pooler connection string."""
    db_url = os.environ["SUPABASE_DB_URL"]
    return psycopg2.connect(db_url)


def init_db() -> None:
    """Apply schema.sql against the configured database."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path) as f:
        schema = f.read()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(schema)
        conn.commit()
    finally:
        conn.close()


def fetchone_dict(query: str, params: tuple = ()) -> dict[str, Any] | None:
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def fetchall_dict(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def execute(query: str, params: tuple = ()) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
        conn.commit()
    finally:
        conn.close()
