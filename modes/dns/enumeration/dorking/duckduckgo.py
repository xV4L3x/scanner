from ... import utility
from duckduckgo_search import DDGS



def duckduckgo(dork, args):

    print("Dorking from duckduckgo...")
    print("Executing query " + dork)

    results = []
    search_results = DDGS().text(dork, max_results=100)
    for search_result in search_results:
        url = search_result["href"]
        # extract the domain from the url
        subdomain = url.split("/")[2]
        subdomain_ip = utility.check_domain_ip(subdomain)
        results.append(subdomain)
        utility.output(args, (subdomain, subdomain_ip), False)
