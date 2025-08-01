import sqlite3
import functools

query_cache = {}

def cache_query(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        query = kwargs.get('query') if 'query' in kwargs else (args[0] if args else None)
        if query in query_cache:
            print(f"[cache] hit for {query}")
            return query_cache[query]

        result = func(conn, *args, **kwargs)
        query_cache[query] = result
        print(f"[cache] set for {query}")
        return result
    return wrapper

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

if __name__ == "__main__":
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print(users)
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print(users_again)
