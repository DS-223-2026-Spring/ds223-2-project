import psycopg2
import os
from dotenv import load_dotenv
# -------------------------
# CONNECTION
# -------------------------

load_dotenv()

def get_connection():
    """Same host/db env conventions as `db_utils` (POSTGRES_HOST in Docker, DB_HOST on laptop)."""
    host = os.environ.get("POSTGRES_HOST") or os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT") or os.environ.get("DB_PORT", "5432")
    password = os.environ.get("DB_PASSWORD") or os.environ.get("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError("Set DB_PASSWORD (or POSTGRES_PASSWORD) for database access.")
    return psycopg2.connect(
        host=host,
        database=os.environ.get("DB_NAME", "marketing_db"),
        user=os.environ.get("DB_USER", os.environ.get("POSTGRES_USER", "postgres")),
        password=password,
        port=port,
    )
# -------------------------
# CREATE (INSERT)
# -------------------------
def insert(cur, table, columns, values, returning=None):
    query = f"""
        INSERT INTO {table} ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(values))})
    """

    if returning:
        query += f" RETURNING {returning}"

    cur.execute(query, values)

    if returning:
        return cur.fetchone()[0]

# -------------------------
# READ (SELECT)
# -------------------------
def select_all(cur, table):
    cur.execute(f"SELECT * FROM {table}")
    return cur.fetchall()

def select_where(cur, table, condition, params):
    query = f"SELECT * FROM {table} WHERE {condition}"
    cur.execute(query, params)
    return cur.fetchall()

# -------------------------
# UPDATE
# -------------------------
def update(cur, table, set_clause, condition, params):
    query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
    cur.execute(query, params)

# -------------------------
# DELETE
# -------------------------
def delete(cur, table, condition, params):
    query = f"DELETE FROM {table} WHERE {condition}"
    cur.execute(query, params)