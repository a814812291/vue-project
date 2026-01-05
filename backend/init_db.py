"""Helper script to initialize the local SQLite cache.

This is invoked by Windows batch helpers to avoid complex inline Python
strings that can be garbled under different code pages.
"""

from app.services import cache


def main() -> None:
    cache.init_db()
    print("DB ready at backend/app/data/cache.db")


if __name__ == "__main__":
    main()
