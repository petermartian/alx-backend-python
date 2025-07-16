
from seed import connect_to_prodev

def stream_users():
    """
    Generator that yields one user row (as a dict) at a time
    from the user_data table.
    """
    conn = connect_to_prodev()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data;")
    # Single loop — fetch & yield each row
    for row in cursor:
        yield row
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # Example usage: print every user.
    for user in stream_users():
        print(user)
