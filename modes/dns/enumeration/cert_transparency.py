import requests
from .. import utility


def cert_transparency(args, domain, max_threads):
    print("\nPerforming certificate transparency search (passive)...")

    sources = {
        "crt.sh": "https://crt.sh/?q=" + domain + "&output=json"
    }

    # check if the -s flag is present for data sources
    if "-s" not in args:
        data_sources = ["crt.sh"]
    else:
        # check if the value is all
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

        # get the url for the data source
        url = sources[source]

        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print("Failed to retrieve data from " + source)
                continue
        except requests.exceptions.RequestException as e:
            print("Failed to retrieve data from " + source)
            continue

        # parse the json response
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
