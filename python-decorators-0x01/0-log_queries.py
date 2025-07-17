import sqlite3
import functools
from datetime import datetime

def log_queries(func):
    """Decorator that logs the SQL query with a timestamp before executing."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # extract the SQL string
        query = kwargs.get('query') if 'query' in kwargs else (args[0] if args else None)
        ts = datetime.now().isoformat(sep=' ', timespec='seconds')
        print(f"[{ts}] Executing SQL query: {query}")
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print(users)
