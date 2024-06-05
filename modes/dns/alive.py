import utility


def output(args, domain):
    if "-o" in args:
        file = args[args.index("-o") + 1]
        with open(file, "a") as f:
            f.write(domain + "\n")

    print(domain)


def main(args, threads):
    domains = utility.get_domains_from_input(args)

    # check if domains are alive
    for domain in domains:
        domain = domain.strip()

        if not utility.validate_domain(domain):
            continue

        ip = utility.check_domain_ip(domain)
        if ip is not None:
            output(args, domain)
