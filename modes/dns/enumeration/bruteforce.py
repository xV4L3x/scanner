from .. import utility
import concurrent.futures


def bruteforce(args, domain, max_threads):
    print("\nPerforming bruteforce attack (active)")

    # check if wordlist is present and valid
    wordlist = utility.check_wordlist(args)

    # open the wordlist file
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

