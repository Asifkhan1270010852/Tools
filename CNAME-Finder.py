#!/usr/bin/env python3
# Yeh tool subdomains list lega, har subdomain ka DNS lookup karega
# Agar subdomain CNAME h to sirf uska target output karega (subdomain name nahi)

import concurrent.futures
import dns.resolver
import sys

# Function jo CNAME target return karega
def get_cname_target(subdomain):
    try:
        answers = dns.resolver.resolve(subdomain, 'CNAME')
        for rdata in answers:
            return str(rdata.target)  # Sirf target return karo
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.LifetimeTimeout, dns.resolver.NoNameservers):
        return None
    except Exception:
        return None

def main():
    if len(sys.argv) != 3:
        print(f"Use kaise kare: {sys.argv[0]} subdomains.txt output.txt")
        sys.exit(1)

    input_file = sys.argv[1]   # Subdomains list file
    output_file = sys.argv[2]  # Output file

    with open(input_file, 'r') as f:
        subdomains = [line.strip() for line in f if line.strip()]

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(get_cname_target, sub): sub for sub in subdomains}
        for future in concurrent.futures.as_completed(futures):
            cname_target = future.result()
            if cname_target:
                results.append(cname_target)
                print(cname_target)  # Sirf CNAME target print

    with open(output_file, 'w') as f:
        for cname in results:
            f.write(f"{cname}\n")

    print(f"\n[+] Total {len(results)} CNAME targets mile. Save ho gaye file: {output_file}")

if __name__ == "__main__":
    main()
