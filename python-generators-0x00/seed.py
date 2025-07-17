#!/usr/bin/env python3
import sys
import csv
import uuid
import mysql.connector
from mysql.connector import errorcode

def connect_db():
    """Connect to MySQL server (no database)."""
    try:
        return mysql.connector.connect(
            host="localhost",
            user="peter",
            password="idoit4dalow"
        )
    except mysql.connector.Error as err:
        print(f"[connect_db] {err}")
        return None

def create_database(conn):
    """Create the ALX_prodev database if it doesn't exist."""
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        print("✔️  Database ALX_prodev ready")
    except mysql.connector.Error as err:
        print(f"[create_database] {err}")
        sys.exit(1)
    finally:
        cursor.close()

def connect_to_prodev():
    """Connect to the ALX_prodev database."""
    try:
        return mysql.connector.connect(
            host="localhost",
            user="peter",
            password="idoit4dalow",
            database="ALX_prodev"
        )
    except mysql.connector.Error as err:
        print(f"[connect_to_prodev] {err}")
        return None

def create_table(conn):
    """Create the user_data table if it doesn't exist."""
    stmt = """
    CREATE TABLE IF NOT EXISTS user_data (
        user_id CHAR(36) PRIMARY KEY,
        name    VARCHAR(255) NOT NULL,
        email   VARCHAR(255) NOT NULL,
        age     INT NOT NULL
    );
    """
    cursor = conn.cursor()
    cursor.execute(stmt)
    conn.commit()
    cursor.close()
    print("✔️  Table user_data created")

def insert_data(conn, csv_path):
    """Load CSV and insert rows (generate user_id if missing)."""
    cursor = conn.cursor()
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # use existing user_id if present, otherwise generate one
            uid = row.get("user_id") or str(uuid.uuid4())
            cursor.execute(
                """
                INSERT IGNORE INTO user_data
                  (user_id, name, email, age)
                VALUES (%s, %s, %s, %s)
                """,
                (uid, row["name"], row["email"], row["age"])
            )
    conn.commit()
    cursor.close()
    print(f"✔️  Loaded data from {csv_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python seed.py user_data.csv")
        sys.exit(1)

    csv_file = sys.argv[1]

    # 1) connect & ensure database exists
    root_conn = connect_db()
    if not root_conn:
        sys.exit(1)
    create_database(root_conn)
    root_conn.close()

    # 2) connect to ALX_prodev, create table, load CSV
    prod_conn = connect_to_prodev()
    if not prod_conn:
        sys.exit(1)
    create_table(prod_conn)
    insert_data(prod_conn, csv_file)
    prod_conn.close()

if __name__ == "__main__":
    main()
