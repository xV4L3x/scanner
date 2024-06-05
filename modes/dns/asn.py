import os
import sys
import concurrent.futures
import socket
import utility
import whotfis_py
import ipaddress
import requests
from bs4 import BeautifulSoup

domain_masks = [
    lambda splitted_ip: "ip{3}.ip-{0}-{1}-{2}".format(splitted_ip[0], splitted_ip[1], splitted_ip[2], splitted_ip[3]),
    lambda splitted_ip: "{0}-{1}-{2}-{3}".format(splitted_ip[0], splitted_ip[1], splitted_ip[2], splitted_ip[3]),
    lambda splitted_ip: "host{3}".format(splitted_ip[0], splitted_ip[1], splitted_ip[2], splitted_ip[3]),
    lambda splitted_ip: "in-addr.arpa",
    lambda splitted_ip: "{0}-{1}-{2}".format(splitted_ip[0], splitted_ip[1], splitted_ip[2], splitted_ip[3]),
]

scanned_ips = []


def reverse_lookup(ip):
    if ip in scanned_ips:
        return None

    global counter
    counter += 1

    try:
        host, aliases, addresses = socket.gethostbyaddr(ip)
        for domain_mask in domain_masks:
            masked_domain = domain_mask(ip.split("."))
            if masked_domain in host:
                return None

        for first_ld in first_lds:
            if first_ld in host:
                print("******************** RELEVANT DOMAIN FOUND ********************")
                print(host + "(" + ip + ")" + " (" + str(counter) + " ip scanned)")
                print("***************************************************************")
                return host
        print(host + "(" + ip + ")" + " (" + str(counter) + " ip scanned)")
        return host
    except socket.herror:
        # print("No hostname found for " + ip)
        return None


counter = 0
first_lds = []


def get_bgp_response(router, mask):

    # Hurricane Electrics Endpoint
    url = "https://bgp.he.net/net/{}/{}".format(router, mask)
    response = requests.get(url).text

    # convert response to html
    soup = BeautifulSoup(response, "html.parser")

    # find all the tables in the html
    tables = soup.find_all("table")
    table = tables[1]

    # find all the rows in the table
    rows = table.find_all("tr")
    results = []
    for row in rows:
        # find all the columns in the row
        columns = row.find_all("td")
        if len(columns) != 3:
            continue
        result = {
            "ip": columns[0].text,
            "ptr": columns[1].text,
            "a": columns[2].text,
        }
        results.append(result)

    a_records = [result for result in results if result["a"] != ""]
    return a_records


def main(args, max_threads):


    # get domains from input file
    domains = utility.get_domains_from_input(args)

    global first_lds
    first_lds = list(set([domain.split(".")[-2] for domain in domains]))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        ips = list(executor.map(utility.check_domain_ip, domains))

    ips = [ip for ip in ips if ip is not None]
    ips = list(set(ips))

    asn_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        for lookup_results in executor.map(whotfis_py.lookup, ips, [whotfis_py.registries.RADB] * len(ips)):
            lookup_results = sorted(lookup_results, key=lambda x: x.mask())
            if len(lookup_results) > 0:
                asn_results.append(lookup_results[-1])

    asn_results = [asn_result for asn_result in asn_results if asn_result.route is not None]
    asn_ranges = [{
        "asn": asn_result.origin,
        "router": asn_result.router(),
        "mask": asn_result.mask(),
    } for asn_result in asn_results]

    #remove duplicates
    asn_ranges = [dict(t) for t in {tuple(d.items()) for d in asn_ranges}]

    for asn_range in asn_ranges:
        print("Scanning " + str(2 ** int(32 - int(asn_range["mask"]))) + " adddresses from " +
              asn_range["asn"] + " (" + asn_range["router"] + "/" + str(asn_range["mask"]) + ")")
        answer = input("continue? y/n: ")
        if answer.lower() != "y":
            continue

        a_records = get_bgp_response(asn_range["router"], asn_range["mask"])
        global scanned_ips
        scanned_ips = [a_record["ip"] for a_record in a_records]

        for a_record in a_records:
            hosts = a_record["a"]
            ip = a_record["ip"]

            for host in hosts.split(","):
                host = host.strip()
                for first_ld in first_lds:
                    if first_ld in host:
                        print("******************** RELEVANT DOMAIN FOUND ********************")
                        print(host + " (" + ip + ")" + " (" + str(counter) + " ip scanned)")
                        print("***************************************************************")
                        return host
                print(host + " (" + ip + ")" + " (" + str(counter) + " ip scanned)")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            executor.map(
                reverse_lookup,
                [str(ip) for ip in ipaddress.IPv4Network(asn_range["router"] + "/" + str(asn_range["mask"]))]),
