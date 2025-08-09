#!/usr/bin/env python3
import sys
import requests
import dns.resolver
import argparse
import json
from tabulate import tabulate

requests.packages.urllib3.disable_warnings()

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
    try:
        r = requests.get(f"http://{domain}", timeout=5, verify=False)
        headers = {k.lower(): v for k, v in r.headers.items()}
        if not any("azurefd-verification" in k for k in headers.keys()):
            return True
        return False
    except requests.RequestException:
        return False

def analyze_domain(target):
    result = {
        "domain": target,
        "cname": None,
        "status": "safe",
        "notes": ""
    }

    cname = get_cname(target)
    if not cname:
        result["notes"] = "No CNAME found"
        return result

    result["cname"] = cname

    if ".azurefd.net" not in cname:
        result["notes"] = "Not AzureFD endpoint"
        return result

    if suffix_present(cname):
        if check_custom_domain_verification(target):
            result["status"] = "vulnerable"
            result["notes"] = "Suffix present, custom domain verification missing → bypass possible"
        else:
            result["notes"] = "Suffix present, verification enabled"
    else:
        status = check_azurefd(cname)
        if status == "default_error":
            result["status"] = "vulnerable"
            result["notes"] = "No suffix, default AzureFD error → dangling endpoint"
        else:
            result["notes"] = "No suffix, endpoint active"

    return result

def main():
    parser = argparse.ArgumentParser(description="Azure Front Door Takeover Detector")
    parser.add_argument("-u", "--url", help="Single domain/subdomain to check")
    parser.add_argument("-l", "--list", help="File with list of domains")
    parser.add_argument("--vuln-only", action="store_true", help="Show only vulnerable domains")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    if not args.url and not args.list:
        parser.print_help()
        sys.exit(1)

    targets = []
    if args.url:
        targets.append(args.url.strip())
    if args.list:
        with open(args.list, "r") as f:
            targets.extend([line.strip() for line in f if line.strip()])

    results = [analyze_domain(target) for target in targets]

    if args.vuln-only:
        results = [r for r in results if r["status"] == "vulnerable"]

    if args.json:
        print(json.dumps(results, indent=4))
    else:
        table = [[r["domain"], r["cname"], r["status"], r["notes"]] for r in results]
        print(tabulate(table, headers=["Domain", "CNAME", "Status", "Notes"]))

if __name__ == "__main__":
    main()
