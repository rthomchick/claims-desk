"""
Week 19 population script — platform_lifecycle rows for RHEL 8, 9, 10.
Applies against the live Supabase project via the pooler connection
(SUPABASE_DB_URL, port 6543). Run after migrate_week19_item4.

Run directly: python -m server.db.populate_week19_platform_lifecycle

Source: Red Hat's product life cycle API.
  access.redhat.com/product-life-cycles/api/v1/products?name=Red%20Hat%20Enterprise%20Linux

Threshold (ADR-016 Decision 4 addendum): standard_support_end is the end
of the last lifecycle phase included in a standard subscription. The API's
own all_phases array tags each phase name with ptype "normal" or
"extended" ("Extended life cycle support (ELS) add-on" and "Extended life
phase" are both add-on/extended). For RHEL 8, 9, and 10 alike, "Maintenance
support" is the last phase tagged ptype "normal" — the selection is fixed
by that tag, not inferred from phase naming.
"""

from __future__ import annotations

from datetime import datetime, timezone

from server.db.client import get_connection

SOURCE_URL = (
    "https://access.redhat.com/product-life-cycles/api/v1/products"
    "?name=Red%20Hat%20Enterprise%20Linux"
)

# (major_version, standard_support_end, phase_name), selected as the last
# phase with ptype "normal" in the API's all_phases array, verified equal
# across all three versions' per-version phase lists.
ROWS = [
    ("8", "2029-05-31", "Maintenance support"),
    ("9", "2032-05-31", "Maintenance support"),
    ("10", "2035-05-31", "Maintenance support"),
]

INSERT = """
insert into platform_lifecycle
    (platform, major_version, standard_support_end, phase_name, source_url, retrieved_at)
values
    (%s, %s, %s, %s, %s, %s)
"""


def populate() -> None:
    retrieved_at = datetime.now(timezone.utc)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for major_version, standard_support_end, phase_name in ROWS:
                print(f"Inserting RHEL {major_version} -> {standard_support_end} ({phase_name})")
                cur.execute(
                    INSERT,
                    (
                        "Red Hat Enterprise Linux",
                        major_version,
                        standard_support_end,
                        phase_name,
                        SOURCE_URL,
                        retrieved_at,
                    ),
                )
        conn.commit()
        print("\nPopulation committed.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    populate()
