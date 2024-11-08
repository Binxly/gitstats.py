#!/usr/bin/env python3
import argparse

from scanner import GitRepositoryScanner
from stats import GitStats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Git Repository Scanner and Stats Visualizer"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan for Git repositories")
    scan_parser.add_argument("path", help="Directory path to scan for Git repositories")

    stats_parser = subparsers.add_parser("stats", help="Show commit statistics")
    stats_parser.add_argument("email", help="Git email address to track commits for")

    args = parser.parse_args()

    if args.command == "scan":
        scanner = GitRepositoryScanner()
        scanner.scan(args.path)
    elif args.command == "stats":
        stats = GitStats()
        stats.print_stats(args.email)


if __name__ == "__main__":
    main()
