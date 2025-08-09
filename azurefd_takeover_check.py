#!/usr/bin/env python3
import sys
import requests
import dns.resolver

def get_cname(domain):
    try:
        answers = dns.resolver.resolve(domain, 'CNAME')
        for rdata in answers:
            return str(rdata.target).strip('.')
    except:
        return None

def check_azurefd(endpoint):
    try:
        r = requests.get(f"https://{endpoint}", timeout=5, verify=False)
        text = r.text.lower()
        if "azure front door" in text or "error 404" in text or "resource you are looking for" in text:
            return "default_error"
        return "active"
    except requests.RequestException:
        return "unreachable"

def suffix_present(cname):
    parts = cname.split(".")[0].split("-")
    if len(parts[-1]) > 10 and any(char.isdigit() for char in parts[-1]):
        return True
    return False

def check_custom_domain_verification(domain):
    """
    AzureFD में custom domain verify न होने पर यह header missing होता है:
    'azurefd-verification'
    """
    try:
        r = requests.get(f"http://{domain}", timeout=5, verify=False)
        headers = {k.lower(): v for k, v in r.headers.items()}
        if not any("azurefd-verification" in k for k in headers.keys()):
            return True  # verification missing → bypass possible
        return False
    except requests.RequestException:
        return False

def main(target):
    cname = get_cname(target)
    if not cname:
        print(f"[!] No CNAME record found for {target}")
        return

    print(f"[*] CNAME: {cname}")

    if ".azurefd.net" not in cname:
        print("[!] This is not an Azure Front Door endpoint.")
        return

    if suffix_present(cname):
        print("[i] AzureFD endpoint has a random suffix → Modern AzureFD")
        # Suffix bypass check
        if check_custom_domain_verification(target):
            print("[+] Custom Domain verification missing → Suffix bypass takeover possible!")
        else:
            print("[-] Custom Domain verification enabled → Safe from suffix bypass")
    else:
        print("[i] AzureFD endpoint has NO random suffix → Old AzureFD style takeover possible if endpoint deleted")

    # Endpoint status
    status = check_azurefd(cname)
    if status == "default_error":
        print("[+] Endpoint returns Azure default error page → Possible dangling endpoint")
    elif status == "active":
        print("[-] Endpoint is active → Takeover not possible")
    else:
        print("[!] Endpoint unreachable")

    # Target domain status
    print(f"[*] Checking {target} directly...")
    status = check_azurefd(target)
    if status == "default_error":
        print("[+] Target domain shows Azure default error page → Takeover candidate")
    elif status == "active":
        print("[-] Target domain is serving active content → Safe")
    else:
        print("[!] Target domain unreachable")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <subdomain>")
        sys.exit(1)

    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    main(sys.argv[1])
