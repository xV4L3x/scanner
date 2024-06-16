from .. import utility
from cryptography import x509
def san(args, domain, max_threads):
    print("\nPerforming Subject Alternative Name (SAN) enumeration (passive)...")

    cert_bin = utility.get_certificate(domain)
    sans = utility.extract_san(cert_bin)

    for name in sans:
        if isinstance(name, x509.DNSName):
            if name.value[0] == "*":
                continue
            utility.output(args, (name.value, utility.check_domain_ip(name.value)), False)