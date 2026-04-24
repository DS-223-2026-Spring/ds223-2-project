import psycopg2
import os
from dotenv import load_dotenv
# -------------------------
# CONNECTION
# -------------------------

load_dotenv()

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