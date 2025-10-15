from __future__ import annotations
import argparse, logging
from .logging_config import init_logging
from .gmail_client import GmailClient
from .fetch_emails import fetch_and_store
from .process_emails import process_with_rules


init_logging()
logger = logging.getLogger(__name__)




def main():
    parser = argparse.ArgumentParser(prog="gmail-rules-processor")
    sub = parser.add_subparsers(dest="cmd", required=True)


    sub.add_parser("auth", help="Run OAuth flow and save token.json")


    p_fetch = sub.add_parser("fetch", help="Fetch inbox emails and store to DB")
    p_fetch.add_argument("--max", type=int, default=100)


    p_proc = sub.add_parser("process", help="Process emails with rules JSON")
    p_proc.add_argument("--rules", required=True)


    args = parser.parse_args()


    if args.cmd == "auth":
        GmailClient().authenticate()
        logger.info("Authentication complete.")
    elif args.cmd == "fetch":
        n = fetch_and_store(max_results=args.max)
        logger.info("Fetched %s new emails", n)
    elif args.cmd == "process":
        n = process_with_rules(args.rules)
        logger.info("Processed %s messages (actions applied)", n)


if __name__ == "__main__":
    main()
