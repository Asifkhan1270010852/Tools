# Tools
Tools And Some Script

## Crt.py 

    python3 crt.py example.com

    python3 crt.py example.com > clean_subdomains.txt


## Shodan 

1. Requirements:

       pip install shodan argparse

2. API Key Setup (Optional but Recommended)
   
    Set your API key as an environment variable to avoid typing every time:

       export SHODAN_API_KEY="your_shodan_api_key"
   
4. Usage:

       python shodan-enum.py -d example.com -o output.txt

## Censys

Features of Tool: 

1. Censys Certs API use karta hai
2. Subdomains extract karta hai
3. Duplicates remove karta hai
4. Output file me save karta hai

Requirements: 
Install dependencies:

     pip install censys python-dotenv

Get your Censys API credentials:

. CENSYS_API_ID

. CENSYS_API_SECRET

Save in a .env file:

    CENSYS_API_ID=your_api_id_here
    CENSYS_API_SECRET=your_api_secret_here

 Usage: 

    python3 censys_enum.py -d example.com -o output.txt


## SecurityTrails

 Tool Features:

. SecurityTrails API use karta hai
. Subdomains extract karta hai
. Duplicate remove karta hai
. Output file me save karta hai
. API key .env file se leta hai


2. Requirements:
   
. Install required libraries:

    pip install requests python-dotenv

Get SecurityTrails API Key:

. Save it in a .env file:

    ST_API_KEY=your_securitytrails_api_key_here

. Usage: 

    python3 securitytrails_enum.py -d example.com -o myoutput.txt


## GITHUB Subdomain Enumeration 

1. Features:

. GitHub Search API ka use karke subdomain enumerate karta hai
. Duplicates remove karta hai
. Token-based authentication support
. Output file save option
. Regex-based filtering (target domain ke liye)

2. API-KEY Add

       GITHUB_TOKEN=your_github_personal_access_token

## Example Usage:

    python github_subdomain_finder.py example.com -o github_result.txt
 
    python github_subdomain_finder.py example.com --token YOUR_GITHUB_TOKEN


## CNAME Finder

     python cname_targets.py subs.txt output.txt


##  subdomain_dedupe_tool

     python3 subdomain_dedupe_tool.py -i all_subs.txt -o unique.txt --normalize --strip-wildcard --sort


## keyword_url_filter.py

     python3 keyword_url_filter.py -i urls.txt -o result.txt -k amazon github shopify


## azurefd_checker.go

    go build azurefd_checker.go

    ./azurefd_checker -l urls.txt 
    
    ./azurefd_checker -l urls.txt --vuln-only


