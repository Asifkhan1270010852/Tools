#!/usr/bin/env python3
"""
subdomain_dedupe_tool.py

A small command-line tool to clean and remove duplicate subdomains common in bug-bounty lists.
Features:
- Read from a file or stdin
- Normalizes entries (strip scheme, path, port, trailing dots)
- Removes wildcard prefixes (*.example.com)
- Optionally decode/encode punycode (IDNA)
- Case-insensitive dedupe
- Preserve original order or sort output
- Prints simple stats

Usage examples:
1) Read from file and write unique sorted output:
   python3 subdomain_dedupe_tool.py -i all_subs.txt -o unique.txt --normalize --sort

2) Read from stdin and print to stdout:
   cat all_subs.txt | python3 subdomain_dedupe_tool.py --normalize > unique.txt

3) Keep original ordering (first occurrence wins):
   python3 subdomain_dedupe_tool.py -i all_subs.txt -o unique.txt --preserve-order

"""

import sys
import argparse
import re
from urllib.parse import urlparse

# Helper functions
RE_IPV4 = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
RE_PORT = re.compile(r":\d+$")


def normalize_host(host: str, strip_wildcard: bool = True, punycode: bool = False) -> str:
    """Normalize a host string:
    - strip scheme and path
    - remove trailing slashes and dots
    - remove port numbers
    - optionally remove leading '*.'
    - lowercase
    - optionally convert IDN/Punycode to ascii form
    """
    host = host.strip()
    if not host:
        return ""

    # If it's a URL, parse it
    if host.startswith(('http://', 'https://', 'ftp://')):
        try:
            p = urlparse(host)
            host = p.hostname or host
        except Exception:
            pass

    # Remove URL paths if someone pasted full URLs
    if '/' in host:
        host = host.split('/')[0]

    # Remove query or fragments
    host = host.split('?')[0].split('#')[0]

    # Remove port
    host = RE_PORT.sub('', host)

    # Remove trailing dots
    host = host.rstrip('.')

    # Remove leading wildcard
    if strip_wildcard and host.startswith('*.'):
        host = host[2:]

    host = host.lower()

    # If it's an IPv4 address, return as-is
    if RE_IPV4.match(host):
        return host

    # Normalize IDN/punycode if requested
    if punycode:
        try:
            # encode unicode -> idna (ASCII punycode)
            host = host.encode('idna').decode('ascii')
        except Exception:
            pass

    return host


def read_lines(source):
    if source == '-':
        for line in sys.stdin:
            yield line.rstrip('\n')
    else:
        with open(source, 'r', encoding='utf-8', errors='ignore') as fh:
            for line in fh:
                yield line.rstrip('\n')


def write_lines(dest, lines):
    if dest == '-':
        for l in lines:
            sys.stdout.write(l + '\n')
    else:
        with open(dest, 'w', encoding='utf-8') as fh:
            for l in lines:
                fh.write(l + '\n')


def main():
    parser = argparse.ArgumentParser(description='Deduplicate and normalize subdomain lists (bug-bounty friendly).')
    parser.add_argument('-i', '--input', help='Input file (use - for stdin)', default='-')
    parser.add_argument('-o', '--output', help='Output file (use - for stdout)', default='-')
    parser.add_argument('--normalize', help='Normalize entries (strip schemes/paths/ports, lowercase)', action='store_true')
    parser.add_argument('--strip-wildcard', help='Strip leading "*."', action='store_true')
    parser.add_argument('--punycode', help='Convert unicode to ASCII punycode (idna)', action='store_true')
    parser.add_argument('--sort', help='Sort output alphabetically', action='store_true')
    parser.add_argument('--preserve-order', help='Preserve first-seen order instead of sorting', action='store_true')
    parser.add_argument('--remove-ips', help='Remove plain IPv4 entries', action='store_true')
    parser.add_argument('--case-sensitive', help='Make dedupe case-sensitive (default: case-insensitive)', action='store_true')

    args = parser.parse_args()

    raw_count = 0
    seen = set()
    output = []

    for line in read_lines(args.input):
        raw_count += 1
        if not line:
            continue
        original = line.strip()

        # Basic cleanup: remove surrounding whitespace & quotes
        entry = original.strip(' \"\'')

        if args.normalize:
            entry = normalize_host(entry, strip_wildcard=args.strip_wildcard, punycode=args.punycode)

        if not entry:
            continue

        # Optionally remove IPv4 entries
        if args.remove_ips and RE_IPV4.match(entry):
            continue

        key = entry if args.case_sensitive else entry.lower()

        if key in seen:
            continue

        seen.add(key)
        output.append(entry)

    # Sorting / preserving order
    if args.sort and not args.preserve_order:
        output = sorted(output)

    # Write out
    write_lines(args.output, output)

    # Print stats to stderr
    kept = len(output)
    dropped = raw_count - kept
    sys.stderr.write(f"Processed: {raw_count}\n")
    sys.stderr.write(f"Kept: {kept}\n")
    sys.stderr.write(f"Dropped (likely duplicates/filtered): {dropped}\n")


if __name__ == '__main__':
    main()
