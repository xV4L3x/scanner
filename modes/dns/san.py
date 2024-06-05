import utility
import concurrent.futures
from cryptography import x509


def main(args, max_threads):
    domains = utility.get_domains_from_input(args)

    # get certificates for all domains
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        certificates_bin = list(executor.map(utility.get_certificate, domains))

    certificates_bin = [certificate_bin for certificate_bin in certificates_bin if certificate_bin is not None]
    # get the sans from the certificates
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        sans_lists = list(executor.map(utility.extract_san, certificates_bin))

    counter = 0
    for sans in sans_lists:
        for name in sans:
            if isinstance(name, x509.DNSName):
                if name.value[0] == "*":
                    continue
                print(name.value)
                counter += 1

    print(counter)


