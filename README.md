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















