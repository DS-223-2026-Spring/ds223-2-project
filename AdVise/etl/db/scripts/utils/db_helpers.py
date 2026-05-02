import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# CONNECTION
# -------------------------
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

# -------------------------
# CREATE (INSERT)
# -------------------------
def insert(cur, table, columns, values, returning=None):
    cols = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(values))

    query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

    if returning:
        query += f" RETURNING {returning}"

    cur.execute(query, values)

    if returning:
        return cur.fetchone()[0]

# -------------------------
# READ
# -------------------------
def select_all(cur, table):
    cur.execute(f"SELECT * FROM {table}")
    return cur.fetchall()

def select_where(cur, table, condition, params):
    query = f"SELECT * FROM {table} WHERE {condition}"
    cur.execute(query, params)
    return cur.fetchall()

# -------------------------
# UPDATE (cleaner abstraction)
# -------------------------
def update(cur, table, data: dict, condition, params):
    set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
    values = list(data.values())

    query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
    cur.execute(query, values + params)

# -------------------------
# DELETE
# -------------------------
def delete(cur, table, condition, params):
    query = f"DELETE FROM {table} WHERE {condition}"
    cur.execute(query, params)