import sqlite3
import functools

def transactional(func):
    """Decorator that wraps a function in a transaction (commit/rollback)."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            print(f"Rolled back due to: {e}")
            raise
        finally:
            conn.close()
    return wrapper

@transactional
def add_user(conn, username, email):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email) VALUES (?, ?)",
        (username, email)
    )
    return cursor.lastrowid

if __name__ == "__main__":
    try:
        new_id = add_user(username="jdoe", email="jdoe@example.com")
        print(f"Inserted user with ID {new_id}")
    except:
        print("Insert failed.") 
