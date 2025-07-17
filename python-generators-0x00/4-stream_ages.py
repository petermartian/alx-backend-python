
from seed import connect_to_prodev


def stream_user_ages():
    """
    Generator that yields one user age at a time from the database.
    """
    conn = connect_to_prodev()
    cursor = conn.cursor()
    cursor.execute("SELECT age FROM user_data;")
    for (age,) in cursor:
        yield age
    cursor.close()
    conn.close()


def average_age():
    """
    Calculate and print the average age without loading all rows into memory.
    Uses the stream_user_ages generator.
    """
    total = 0
    count = 0
    for age in stream_user_ages():
        total += age
        count += 1
    avg = (total / count) if count else 0
    print(f"Average age of users: {avg:.2f}")


if __name__ == "__main__":
    average_age()
