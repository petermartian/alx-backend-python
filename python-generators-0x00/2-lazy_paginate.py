
from seed import connect_to_prodev


def paginate_users(page_size, offset):
    """
    Helper that fetches a single page of users from the database.
    Returns a list of dicts (may be empty).
    """
    conn = connect_to_prodev()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM user_data LIMIT %s OFFSET %s",
        (page_size, offset)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def lazy_paginate(page_size):
    """
    Generator that lazily loads pages of users.
    Yields one page (list of dicts) at a time.
    Uses only one loop internally.
    """
    offset = 0
    # Single loop to fetch page after page
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size


if __name__ == "__main__":
    import sys
    # allow page size from command line
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    # print each user in each page
    try:
        for page in lazy_paginate(size):
            for user in page:
                print(user)
    except BrokenPipeError:
        # handle piping out
        pass
