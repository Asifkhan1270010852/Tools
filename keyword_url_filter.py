#!/usr/bin/env python3
"""
keyword_url_filter.py

Filter and deduplicate URLs by specific keywords.

Usage:
    python3 keyword_url_filter.py -i input.txt -o output.txt -k amazon github shopify
"""

import argparse
import sys

def read_lines(file_path):
    if file_path == "-":
        for line in sys.stdin:
            yield line.strip()
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                yield line.strip()

def write_lines(file_path, lines):
    if file_path == "-":
        for line in lines:
            print(line)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

def main():
    parser = argparse.ArgumentParser(description="Filter and deduplicate URLs by keywords.")
    parser.add_argument("-i", "--input", default="-", help="Input file (or - for stdin)")
    parser.add_argument("-o", "--output", default="-", help="Output file (or - for stdout)")
    parser.add_argument("-k", "--keywords", nargs="+", required=True, help="Keywords to match in URLs")
    parser.add_argument("--case-sensitive", action="store_true", help="Case-sensitive keyword match")
    args = parser.parse_args()

    keywords = args.keywords if args.case_sensitive else [k.lower() for k in args.keywords]
    seen = set()
    filtered = []

    for url in read_lines(args.input):
        if not url:
            continue
        check_url = url if args.case_sensitive else url.lower()
        if any(k in check_url for k in keywords):
            if check_url not in seen:
                seen.add(check_url)
                filtered.append(url)

    write_lines(args.output, filtered)

    sys.stderr.write(f"Processed: {len(seen)} unique matching URLs found\\n")

if __name__ == "__main__":
    main()
