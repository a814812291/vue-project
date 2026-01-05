import argparse
import logging

from app.services import cache
from app.services.refresh_service import refresh

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Refresh limit up cache")
    parser.add_argument("--date", default="auto", help="trade date, e.g. 20240101 or auto")
    args = parser.parse_args()
    target_date, items = refresh(args.date)
    logging.info("refresh done for %s, %s rows", target_date, len(items))


if __name__ == "__main__":
    main()
