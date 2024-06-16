from .hackertarget import hackertarget
from .dnsdumpster import dnsdumpster
from .anubis_db import anubis_db

HACKERTARGET = "hackertarget"
DNS_DUMPSTER = "dnsdumpster"
ANUBIS_DB = "anubis-db"


def data_sources(domain):
    return {
        HACKERTARGET: "https://api.hackertarget.com/hostsearch/?q=" + domain,
        ANUBIS_DB: "https://jonlu.ca/anubis/subdomains/" + domain
    }


methods = {
    HACKERTARGET: hackertarget,
    DNS_DUMPSTER: dnsdumpster,
    ANUBIS_DB: anubis_db
}


def main(args, domain, max_threads):
    print("\nPerforming DNS aggregation search (passive)...")

    # check if the -sE flag is present for search engines
    if "-dSE" not in args:
        search_engines = [HACKERTARGET]
    else:
        # check if the value is all
        if args[args.index("-dSE") + 1] == "all":
            search_engines = methods.keys()
        else:
            search_engines = args[args.index("-dSE") + 1].split(",")

    def getUrl(search_engine):
        if search_engine in data_sources(domain):
            return data_sources(domain)[search_engine]
        else:
            return None

    for search_engine in search_engines:
        # get the url for the data source
        methods[search_engine](domain, args,getUrl(search_engine))
