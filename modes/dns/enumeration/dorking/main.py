from .duckduckgo import duckduckgo

DUCK_DUCK_GO = "duckduckgo"
methods = {
    DUCK_DUCK_GO: duckduckgo,
}


def dorks(domain):
    dorks = {
        DUCK_DUCK_GO: "site:" + domain
    }
    return dorks


def main(args, domain, max_threads):
    print("\nPerforming dorking search (passive)...")

    # check if the -sE flag is present for search engines
    if "-sE" not in args:
        search_engines = [DUCK_DUCK_GO]
    else:
        # check if the value is all
        if args[args.index("-sE") + 1] == "all":
            search_engines = dorks(domain).keys()
        else:
            search_engines = args[args.index("-sE") + 1].split(",")

    for search_engine in search_engines:
        methods[search_engine](dorks(domain)[search_engine], args)
