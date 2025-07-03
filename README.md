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

       python shodan.py -d example.com -o output.txt
