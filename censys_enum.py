import os
import argparse
from dotenv import load_dotenv
from censys.search import CensysCerts
from censys.common.exceptions import CensysException

def banner():
    print("""
   ____                               
  / ___|___  _ __ ___  _ __ ___  ___  
 | |   / _ \| '_ ` _ \| '__/ _ \/ __| 
 | |__| (_) | | | | | | | |  __/\__ \ 
  \____\___/|_| |_| |_|_|  \___||___/ 
                                      
      Subdomain Finder via Censys
    """)

def load_api():
    load_dotenv()
    api_id = os.getenv("CENSYS_API_ID")
    api_secret = os.getenv("CENSYS_API_SECRET")
    if not api_id or not api_secret:
        print("[!] Missing CENSYS API credentials.")
        exit(1)
    return api_id, api_secret

def find_subdomains(domain, api_id, api_secret):
    try:
        c = CensysCerts(api_id=api_id, api_secret=api_secret)
        query = f'parsed.names: {domain}'
        print(f"[*] Searching Censys for domain: {domain}")
        results = c.search(query=query, fields=["parsed.names"], max_records=1000)

        subdomains = set()
        for result in results:
            names = result.get("parsed.names", [])
            for name in names:
                if name.endswith(domain):
                    subdomains.add(name.lower())

        return sorted(subdomains)
    except CensysException as e:
        print(f"[!] Censys Error: {e}")
        return []

def save_output(subdomains, output):
    with open(output, "w") as f:
        for sub in subdomains:
            f.write(sub + "\n")
    print(f"[+] Saved {len(subdomains)} subdomains to {output}")

def main():
    banner()
    parser = argparse.ArgumentParser(description="Censys Subdomain Enumerator")
    parser.add_argument("-d", "--domain", required=True, help="Target domain (e.g. example.com)")
    parser.add_argument("-o", "--output", default="censys_subdomains.txt", help="Output file")
    args = parser.parse_args()

    api_id, api_secret = load_api()
    subdomains = find_subdomains(args.domain, api_id, api_secret)

    if subdomains:
        print("\n[+] Subdomains found:")
        for sub in subdomains:
            print(f" - {sub}")
        save_output(subdomains, args.output)
    else:
        print("[!] No subdomains found.")

if __name__ == "__main__":
    main()
