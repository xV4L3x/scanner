from .. import utility
import sys
import re
from .bruteforce import bruteforce
from .cert_transparency import cert_transparency
from .dorking.main import main as dorking
from .dns_aggregators.main import main as dns_aggregators
from .san import san

BRUTEFORCE_MODE = 0
CERT_TRANSPARENCY_MODE = 1
DORKING_MODE = 2
DNS_AGGREGATORS_MODE = 3
SAN = 4

enumeration_methods = {
    BRUTEFORCE_MODE: bruteforce,
    CERT_TRANSPARENCY_MODE: cert_transparency,
    DORKING_MODE: dorking,
    DNS_AGGREGATORS_MODE: dns_aggregators,
    SAN: san
}


def main(args, max_threads):
    # check if there is the -d flag along with the domain
    if "-d" in args:
        domain = args[args.index("-d") + 1]
        # check if the domain is valid with regex
        valid = utility.validate_domain(domain)
        if not valid:
            print("Invalid domain")
            sys.exit(1)
    else:
        print("Usage: python main.py dns -d <domain>")
        sys.exit(1)

    # get the ip address of the domain
    ip = utility.check_domain_ip(domain)
    if ip is None:
        print("Domain not reachable")
        if "-r" in args:
            return []
        sys.exit(1)
    print("Checking DNS services for domain: " + domain + " (" + ip + ")")

    print("\nEnumerating subdomains of " + domain)

    if "-m" in args:
        modes = args[args.index("-m") + 1]
        if modes == "all":
            modes = enumeration_methods.keys()
        else:
            # check that the mode is either an int or a list of ints separated by commas
            if not re.match(r"^\d+(?:,\d+)*$", modes):
                print("Invalid enumeration mode")
                sys.exit(1)
            # convert the mode to a list of ints
            modes = list(map(int, modes.split(",")))
    else:
        # default to brute force mode
        modes = [0]

    # execute enumeration for each mode
    for mode in modes:
        if mode not in enumeration_methods:
            print("Invalid enumeration mode:" + str(mode))
            continue
        enumeration_methods[mode](args, domain, max_threads)

    # remove duplicate lines from the output file
    domains_found = []
    if "-o" in args:
        file = args[args.index("-o") + 1]
        with open(file, "r") as f:
            lines = f.readlines()
        with open(file, "w") as f:
            domains_found = sorted(set(lines))
            f.writelines(domains_found)

    # check if -r flag is present for recursive enumeration
    if "-r" in args:
        # get recursive depth
        depth = args[args.index("-r") + 1]
        if not depth.isdigit():
            print("Invalid depth")
            sys.exit(1)

        depth = int(depth)

        # execute recursive enumeration
        if depth > 1:
            for domain in domains_found:
                domain = domain.strip()

                if domain in domains_found or domain[0] == "*":
                    continue

                new_args = args.copy()
                new_args[args.index("-d") + 1] = domain
                new_args[args.index("-r") + 1] = str(int(depth) - 1)

                recursive_domains_found = main(new_args, max_threads)

                # add the new domains found to the list
                for recursive_domain in recursive_domains_found:
                    if recursive_domain not in domains_found:
                        domains_found.append(recursive_domain)



    print("\nDone")
    return domains_found
