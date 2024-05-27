import sys
import os
import utility


def output(args, domain):
    if "-o" in args:
        file = args[args.index("-o") + 1]
        with open(file, "a") as f:
            f.write(domain + "\n")
    
    print(domain)

def main(args, threads):
    #check if -i flag is present for input file
    if "-i" in args:
        file = args[args.index("-i") + 1]
        if not os.path.exists(file):
            print("Input file " + file + " does not exist")
            sys.exit(1)
        with open(file, "r") as f:
            domains = f.readlines()
    else:
        domains = args

    #check if domains are alive
    for domain in domains:
        domain = domain.strip()

        if not utility.validate_domain(domain):
            continue

        ip = utility.check_domain_ip(domain)
        if ip is not None:
            output(args, domain)