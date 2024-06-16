from dnsdumpster.DNSDumpsterAPI import DNSDumpsterAPI
from ... import utility
def dnsdumpster(domain, args, url):
    print("\nChecking dnsdumpster...")

    results = DNSDumpsterAPI().search(domain)
    results = results["dns_records"]["host"]

    for result in results:
        subdomain = result["domain"]
        ip = result["ip"]
        utility.output(args, (subdomain, ip), False)