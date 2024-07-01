import base64
import requests
import codecs
import mmh3
from shodan import Shodan
from dotenv import load_dotenv
import os


def favicon(args, domain, max_threads):


    load_dotenv()

    print("\nPerforming favicon search (passive)...")
    return;


    https_domain = "https://" + domain + "/favicon.ico"
    http_domain = "http://" + domain + "/favicon.ico"

    urls = [https_domain, http_domain]

    favicon_hashes = ["72b36155"]
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue
        except requests.exceptions.RequestException as e:
            continue

        #get base64 encoded favicon
        favicon = codecs.encode(response.content, "base64")
        hash = mmh3.hash(favicon)

        if hash in favicon_hashes:
            continue

        favicon_hashes.append(hash)
        print("\nFavicon found at: " + url)
        print("Favicon hash: " + str(hash))

    for favicon_hash in favicon_hashes:
        url = "https://api.criminalip.io/v1/banner/search"
        headers = {
            "x-api-key": os.getenv("CRIMINAL_IP_API_KEY")
        }
        params = {
            "query": "favicon : {}".format(favicon_hash),
            "offset": 0
        }

        response = requests.request("GET", url, params=params, headers=headers)
        response = response.json()
        print(response)
        return

