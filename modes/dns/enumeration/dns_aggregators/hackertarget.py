
import requests
from ... import utility
def hackertarget(domain, args, url):
    print("\nChecking hackertarget...")
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
        if len(data.split(",")) < 2:
            continue
        subdomain = data.split(",")[0]
        ip = data.split(",")[1]

        utility.output(args, (subdomain, ip), False)