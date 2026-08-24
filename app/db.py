import logging
import psycopg2
import psycopg2.extras
from app.config import config
from app.models import SearchProfile

logger = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(config.database_url)


def init_schema() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    chat_id              BIGINT PRIMARY KEY,
                    origin_airports      TEXT[]      NOT NULL DEFAULT '{}',
                    destination_airports TEXT[]      NOT NULL DEFAULT '{}',
                    depart_from          DATE,
                    depart_to            DATE,
                    trip_length_min      INT         NOT NULL DEFAULT 7,
                    trip_length_max      INT         NOT NULL DEFAULT 14,
                    adults               INT         NOT NULL DEFAULT 2,
                    children_ages        INT[]       NOT NULL DEFAULT '{}',
                    max_connections      INT         NOT NULL DEFAULT 3,
                    watch_enabled        BOOL        NOT NULL DEFAULT FALSE,
                    last_watch_run       TIMESTAMPTZ,
                    created_at           TIMESTAMPTZ DEFAULT NOW(),
                    updated_at           TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT NOT NULL DEFAULT 'en'")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS active_profile_slot INT NOT NULL DEFAULT 1")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id                   SERIAL PRIMARY KEY,
                    chat_id              BIGINT NOT NULL REFERENCES users(chat_id),
                    slot                 INT NOT NULL,
                    name                 TEXT NOT NULL DEFAULT 'Profile 1',
                    origin_airports      TEXT[]      NOT NULL DEFAULT '{}',
                    destination_airports TEXT[]      NOT NULL DEFAULT '{}',
                    depart_from          DATE,
                    depart_to            DATE,
                    trip_length_min      INT         NOT NULL DEFAULT 7,
                    trip_length_max      INT         NOT NULL DEFAULT 14,
                    adults               INT         NOT NULL DEFAULT 2,
                    children_ages        INT[]       NOT NULL DEFAULT '{}',
                    max_connections      INT         NOT NULL DEFAULT 3,
                    watch_enabled        BOOL        NOT NULL DEFAULT FALSE,
                    last_watch_run       TIMESTAMPTZ,
                    created_at           TIMESTAMPTZ DEFAULT NOW(),
                    updated_at           TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(chat_id, slot)
                )
            """)
            cur.execute("""
                INSERT INTO profiles (
                    chat_id, slot, name,
                    origin_airports, destination_airports,
                    depart_from, depart_to,
                    trip_length_min, trip_length_max,
                    adults, children_ages, max_connections,
                    watch_enabled, last_watch_run
                )
                SELECT
                    chat_id, 1, 'Profile 1',
                    origin_airports, destination_airports,
                    depart_from, depart_to,
                    trip_length_min, trip_length_max,
                    adults, children_ages, max_connections,
                    watch_enabled, last_watch_run
                FROM users
                ON CONFLICT (chat_id, slot) DO NOTHING
            """)
        conn.commit()
    logger.info("Database schema initialised")


def _merged_select(cur, chat_id: int) -> dict | None:
    cur.execute("""
        SELECT u.chat_id, u.language, u.active_profile_slot,
               p.id AS profile_id, p.slot, p.name,
               p.origin_airports, p.destination_airports,
               p.depart_from, p.depart_to,
               p.trip_length_min, p.trip_length_max,
               p.adults, p.children_ages, p.max_connections,
               p.watch_enabled, p.last_watch_run
        FROM users u
        JOIN profiles p ON p.chat_id = u.chat_id AND p.slot = u.active_profile_slot
        WHERE u.chat_id = %s
    """, (chat_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def get_or_create_user(chat_id: int) -> dict:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO users (chat_id) VALUES (%s)
                ON CONFLICT (chat_id) DO NOTHING
            """, (chat_id,))
            cur.execute("""
                INSERT INTO profiles (chat_id, slot, name)
                VALUES (%s, 1, 'Profile 1')
                ON CONFLICT (chat_id, slot) DO NOTHING
            """, (chat_id,))
            row = _merged_select(cur, chat_id)
        conn.commit()
    return row


def get_user(chat_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
            row = cur.fetchone()
    return dict(row) if row else None


def get_active_profile(chat_id: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            row = _merged_select(cur, chat_id)
    return row


def get_all_profiles(chat_id: int) -> list[dict]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM profiles WHERE chat_id = %s ORDER BY slot",
                (chat_id,),
            )
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def create_profile(chat_id: int, slot: int, name: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO profiles (chat_id, slot, name) VALUES (%s, %s, %s)",
                (chat_id, slot, name),
            )
        conn.commit()


def delete_profile(chat_id: int, slot: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM profiles WHERE chat_id = %s AND slot = %s",
                (chat_id, slot),
            )
        conn.commit()


def set_active_profile(chat_id: int, slot: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET active_profile_slot = %s, updated_at = NOW() WHERE chat_id = %s",
                (slot, chat_id),
            )
        conn.commit()


def set_language(chat_id: int, lang: str) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET language = %s, updated_at = NOW() WHERE chat_id = %s",
                (lang, chat_id),
            )
        conn.commit()


def update_profile(chat_id: int, slot: int, **fields) -> None:
    if not fields:
        return
    set_clauses = ", ".join(f"{k} = %s" for k in fields)
    set_clauses += ", updated_at = NOW()"
    values = list(fields.values()) + [chat_id, slot]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE profiles SET {set_clauses} WHERE chat_id = %s AND slot = %s",
                values,
            )
        conn.commit()


def update_user_profile(chat_id: int, **fields) -> None:
    if not fields:
        return
    set_clauses = ", ".join(f"{k} = %s" for k in fields)
    set_clauses += ", updated_at = NOW()"
    values = list(fields.values()) + [chat_id]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""UPDATE profiles SET {set_clauses}
                    WHERE chat_id = %s
                      AND slot = (SELECT active_profile_slot FROM users WHERE chat_id = %s)""",
                values + [chat_id],
            )
        conn.commit()


def set_watch(chat_id: int, slot: int, enabled: bool) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE profiles SET watch_enabled = %s, updated_at = NOW() WHERE chat_id = %s AND slot = %s",
                (enabled, chat_id, slot),
            )
        conn.commit()


def mark_watch_run(chat_id: int, slot: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE profiles SET last_watch_run = NOW(), updated_at = NOW() WHERE chat_id = %s AND slot = %s",
                (chat_id, slot),
            )
        conn.commit()


def get_all_watch_profiles() -> list[dict]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT u.chat_id, u.language, u.active_profile_slot,
                       p.id AS profile_id, p.slot, p.name,
                       p.origin_airports, p.destination_airports,
                       p.depart_from, p.depart_to,
                       p.trip_length_min, p.trip_length_max,
                       p.adults, p.children_ages, p.max_connections,
                       p.watch_enabled, p.last_watch_run
                FROM profiles p
                JOIN users u ON u.chat_id = p.chat_id
                WHERE p.watch_enabled = TRUE
            """)
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def row_to_profile(row: dict) -> SearchProfile:
    return SearchProfile(
        slot=row.get("slot", 1),
        name=row.get("name", "Profile 1"),
        origin_airports=row["origin_airports"] or [],
        destination_airports=row["destination_airports"] or [],
        depart_from=str(row["depart_from"]) if row["depart_from"] else None,
        depart_to=str(row["depart_to"]) if row["depart_to"] else None,
        trip_length_min=row["trip_length_min"],
        trip_length_max=row["trip_length_max"],
        adults=row["adults"],
        children_ages=row["children_ages"] or [],
        max_connections=row["max_connections"],
    )
