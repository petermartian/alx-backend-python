
import sys
from seed import connect_to_prodev


def stream_users_in_batches(batch_size):
    """
    Generator that yields lists of user rows (dicts) in batches of size `batch_size`.
    """
    conn = connect_to_prodev()
    cursor = conn.cursor(dictionary=True)
    offset = 0
    # single loop to fetch in batches
    while True:
        cursor.execute(
            "SELECT * FROM user_data LIMIT %s OFFSET %s",
            (batch_size, offset)
        )
        rows = cursor.fetchall()
        if not rows:
            break
        yield rows
        offset += batch_size

    cursor.close()
    conn.close()


def batch_processing(batch_size):
    """
    Generator that yields individual user rows where age > 25,
    processing each batch from stream_users_in_batches.
    """
    # loop over each batch
    for batch in stream_users_in_batches(batch_size):
        # loop over users in the batch
        for user in batch:
            if user.get('age', 0) > 25:
                yield user


if __name__ == "__main__":
    # allow batch size via CLI, default 50
    size = 50
    if len(sys.argv) > 1:
        try:
            size = int(sys.argv[1])
        except ValueError:
            pass

    for u in batch_processing(size):
        print(u)
