import shodan
import argparse
import os
import sys

def banner():
    print("""
  ____  _               _             
 / ___|| |__   ___  ___| | _____ _ __ 
 \___ \| '_ \ / _ \/ __| |/ / _ \ '__|
  ___) | | | |  __/ (__|   <  __/ |   
 |____/|_| |_|\___|\___|_|\_\___|_|   

     Shodan Subdomain Enumerator
    """)

def load_api_key():
    # API key from environment variable or user input
    api_key = os.getenv("SHODAN_API_KEY")
    if not api_key:
        print("[!] SHODAN_API_KEY environment variable not found.")
        api_key = input("[?] Enter your Shodan API key: ")
    return api_key

def find_subdomains(api_key, domain):
    try:
        api = shodan.Shodan(api_key)
        query = f'hostname:"{domain}"'
        print(f"[*] Searching Shodan for domain: {domain}")
        results = api.search(query)
        
        subdomains = set()
        for result in results['matches']:
            if 'hostnames' in result:
                for hostname in result['hostnames']:
                    if hostname.endswith(domain):
                        subdomains.add(hostname)
        
        return sorted(subdomains)

    except shodan.APIError as e:
        print(f"[!] Shodan API Error: {e}")
        sys.exit(1)

def save_output(subdomains, output_file):
    with open(output_file, 'w') as f:
        for sub in subdomains:
            f.write(sub + '\n')
    print(f"[+] Found {len(subdomains)} subdomains. Saved to {output_file}")

def main():
    banner()
    
    parser = argparse.ArgumentParser(description="Shodan Subdomain Enumerator")
    parser.add_argument("-d", "--domain", required=True, help="Target domain (e.g. example.com)")
    parser.add_argument("-o", "--output", default="shodan_subdomains.txt", help="Output file name")
    
    args = parser.parse_args()

    api_key = load_api_key()
    subdomains = find_subdomains(api_key, args.domain)
    
    if subdomains:
        print("\n[+] Subdomains Found:")
        for sub in subdomains:
            print(f" - {sub}")
        save_output(subdomains, args.output)
    else:
        print("[!] No subdomains found on Shodan.")

if __name__ == "__main__":
    main()
