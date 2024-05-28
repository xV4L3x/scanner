import requests 
import socket
import utility
import threading
import concurrent.futures
import sys
import re

BRUTEFORCE_MODE = 0
CERT_TRANSPARENCY_MODE = 1
DORKING_MODE = 2
DNS_AGGREGATORS_MODE = 3

def bruteforce(args, domain, max_threads):
    print("\nPerforming bruteforce attack (active)")

    #check if wordlist is present and valid        
    wordlist = utility.check_wordlist(args)

    #open the wordlist file
    with open(wordlist) as f:
        lines = f.readlines()

    def enumerate_subdomains(subdomain, domain):
        subdomain = subdomain.strip()
        if subdomain[-1] == ".":
            subdomain = subdomain[:-1]
        subdomain = subdomain + "." + domain

        subdomain_ip = utility.check_domain_ip(subdomain)
        if subdomain_ip is not None:
            utility.output(args, (subdomain, subdomain_ip), True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(enumerate_subdomains, lines, [domain] * len(lines))

def cert_transparency(args, domain, max_threads):

    print("\nPerforming certificate transparency search (passive)...")

    sources = {
        "crt.sh" : "https://crt.sh/?q=" + domain + "&output=json"
    }

    #check if the -s flag is present for data sources
    if "-s" not in args:
        data_sources = ["crt.sh"]
    else:
        #check if the value is all
        if args[args.index("-s") + 1] == "all":
            #TODO ADD OTHER DATA SOURCES
            data_sources = ["crt.sh"]
        else:
            data_sources = args[args.index("-s") + 1].split(",")
            
    
    for source in data_sources:
        if source not in sources:
            print("Unknown data source: " + source)
            continue
        
        print("\nChecking " + source + "...")

        #get the url for the data source
        url = sources[source]

        try:
            response = requests.get(url)
            if response.status_code != 200:
                print("Failed to retrieve data from " + source)
                continue
        except requests.exceptions.RequestException as e:
            print("Failed to retrieve data from " + source)
            continue

        #parse the json response
        try:
            data = response.json()

            for entry in data:
                
                subdomain = entry["name_value"]
                
                if subdomain[0] == "*":
                    continue
            
                subdomain_ip = utility.check_domain_ip(domain)
                utility.output(args, (subdomain, subdomain_ip), False)
                    
                
            

        except ValueError:
            print("Failed to parse JSON from " + source)
            continue

def dorking(args, domain, max_threads):

    print("\nPerforming dorking search (passive)...")

    DUCK_DUCK_GO = "duckduckgo"
    dorks = {
        DUCK_DUCK_GO: "site:" + domain
    }

    def duckduckgo():
        from duckduckgo_search import DDGS

        print("Dorking from duckduckgo...")
        print("Executing query " + dorks[DUCK_DUCK_GO]) 

        results = []
        search_results = DDGS().text(dorks[DUCK_DUCK_GO], max_results=100)
        for search_result in search_results:
            url = search_result["href"]
            #extract the domain from the url
            subdomain = url.split("/")[2]
            subdomain_ip = utility.check_domain_ip(subdomain)
            results.append(subdomain)
            utility.output(args, (subdomain, subdomain_ip), False)

    methods = {
        DUCK_DUCK_GO: duckduckgo,
    }

    #check if the -sE flag is present for search engines
    if "-sE" not in args:
        search_engines = [DUCK_DUCK_GO]
    else:
        #check if the value is all
        if args[args.index("-sE") + 1] == "all":
            search_engines = dorks.keys()
        else:
            search_engines = args[args.index("-sE") + 1].split(",")

    for search_engine in search_engines:
        methods[search_engine]()

def dns_aggregators(args, domain, max_threads):

    print("\nPerforming DNS aggregation search (passive)...")

    HACKERTARGET = "hackertarget"
    DNS_DUMPSTER = "dnsdumpster"
    ANUBIS_DB = "anubis-db"

    data_sources = {
        HACKERTARGET: "https://api.hackertarget.com/hostsearch/?q=" + domain,
        ANUBIS_DB: "https://jonlu.ca/anubis/subdomains/" + domain
    }

    def hackertarget():
        print("\nChecking hackertarget...")
        url = data_sources[HACKERTARGET]
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print("Failed to retrieve data from hackertarget")
                return
        except requests.exceptions.RequestException as e:
            print("Failed to retrieve data from hackertarget")
            return
        
        parsed_data = response.content.splitlines()
        for data in parsed_data:
            data = data.decode("utf-8")
            subdomain = data.split(",")[0]
            ip = data.split(",")[1]

            utility.output(args, (subdomain,ip), False)

    def dnsdumpster():
        print("\nChecking dnsdumpster...")
        from dnsdumpster.DNSDumpsterAPI import DNSDumpsterAPI
        results = DNSDumpsterAPI().search(domain)
        results = results["dns_records"]["host"]

        for result in results:
            subdomain = result["domain"]
            ip = result["ip"]
            utility.output(args, (subdomain,ip), False)

    def anubis_db():
        print("\nChecking anubis-db...")
        url = data_sources[ANUBIS_DB]
        status_codes = [200, 300]
        try:
            print(url)
            response = requests.get(url)
            if response.status_code not in status_codes:
                print("Failed to retrieve data from anubis-db")
                return
        except requests.exceptions.RequestException as e:
            print("Failed to retrieve data from anubis-db")
            return

        data = response.json()
        for subdomain in data:
            ip =  utility.check_domain_ip(subdomain)
            utility.output(args, (subdomain,ip), False)

    methods = {
        HACKERTARGET: hackertarget,
        DNS_DUMPSTER: dnsdumpster,
        ANUBIS_DB: anubis_db
        #whois -h whois.radb.net 34.111.164.191 
    }

    #check if the -sE flag is present for search engines
    if "-dSE" not in args:
        search_engines = [HACKERTARGET]
    else:
        #check if the value is all
        if args[args.index("-dSE") + 1] == "all":
            search_engines = methods.keys()
        else:
            search_engines = args[args.index("-dSE") + 1].split(",")
    
    for search_engine in search_engines:
        #get the url for the data source
        methods[search_engine]()


enumeration_methods = {
    BRUTEFORCE_MODE: bruteforce,
    CERT_TRANSPARENCY_MODE: cert_transparency,
    DORKING_MODE: dorking,
    DNS_AGGREGATORS_MODE: dns_aggregators
}


def main(args, max_threads):
    #check if there is the -d flag along with the domain
    if "-d" in args:
        domain = args[args.index("-d") + 1]
        #check if the domain is valid with regex
        valid = utility.validate_domain(domain)
        if not valid:
            print("Invalid domain")
            sys.exit(1)
    else:
        print("Usage: python main.py dns -d <domain>")
        sys.exit(1)

    
    #get the ip address of the domain
    ip = utility.check_domain_ip(domain)
    if ip is None:
        print("Domain not reachable")
        sys.exit(1)
    print("Checking DNS services for domain: " + domain + " (" + ip + ")")

    


    print("\nEnumerating subdomains of " + domain)

    if "-m" in args:
        modes = args[args.index("-m") + 1]
        if modes == "all":
            modes = enumeration_methods.keys()
        else: 
            #check that the mode is either an int or a list of ints separated by commas
            if not re.match(r"^\d+(?:,\d+)*$", modes):
                print("Invalid enumeration mode")
                sys.exit(1)
            #convert the mode to a list of ints
            modes = list(map(int, modes.split(",")))
    else:
        #default to brute force mode
        modes = [0]

    #execute enumeration for each mode
    for mode in modes:
        if mode not in enumeration_methods:
            print("Invalid enumeration mode:" + mode)
            continue
        enumeration_methods[mode](args, domain, max_threads)


    #remove duplicate lines from the output file
    if "-o" in args:
        file = args[args.index("-o") + 1]
        with open(file, "r") as f:
            lines = f.readlines()
        with open(file, "w") as f:
            f.writelines(sorted(set(lines)))

    print("\nDone")
