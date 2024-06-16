import requests
from ... import utility
def anubis_db(domain, args, url):
    print("\nChecking anubis-db...")
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
        ip = utility.check_domain_ip(subdomain)
        utility.output(args, (subdomain, ip), False)