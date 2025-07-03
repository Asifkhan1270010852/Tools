import os
import requests
import argparse
from dotenv import load_dotenv

def banner():
    print("""
  ____                      _ _         _             
 / ___|  ___  ___ _ __ ___(_) |_ _   _| |_ ___  _ __ 
 \___ \ / _ \/ __| '__/ _ \ | __| | | | __/ _ \| '__|
  ___) |  __/ (__| | |  __/ | |_| |_| | || (_) | |   
 |____/ \___|\___|_|  \___|_|\__|\__,_|\__\___/|_|   

      Subdomain Finder via SecurityTrails
    """)

def load_api_key():
    load_dotenv()
    api_key = os.getenv("ST_API_KEY")
    if not api_key:
        print("[!] SecurityTrails API key not found in environment.")
        exit(1)
    return api_key

def find_subdomains(domain, api_key):
    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    headers = {"APIKEY": api_key}

    try:
        print(f"[*] Searching SecurityTrails for domain: {domain}")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            subdomains = data.get("subdomains", [])
            full_subs = [f"{sub}.{domain}" for sub in subdomains]
            return sorted(set(full_subs))
        else:
            print(f"[!] Error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"[!] Request failed: {e}")
        return []

def save_output(subdomains, output):
    with open(output, "w") as f:
        for sub in subdomains:
            f.write(sub + "\n")
    print(f"[+] Saved {len(subdomains)} subdomains to {output}")

def main():
    banner()
    parser = argparse.ArgumentParser(description="SecurityTrails Subdomain Enumerator")
    parser.add_argument("-d", "--domain", required=True, help="Target domain (e.g. example.com)")
    parser.add_argument("-o", "--output", default="securitytrails_subdomains.txt", help="Output file name")
    args = parser.parse_args()

    api_key = load_api_key()
    subdomains = find_subdomains(args.domain, api_key)

    if subdomains:
        print("\n[+] Subdomains found:")
        for sub in subdomains:
            print(f" - {sub}")
        save_output(subdomains, args.output)
    else:
        print("[!] No subdomains found.")

if __name__ == "__main__":
    main()
