import threading
import re
import sys
import os
import socket
import ssl
import certifi
from cryptography import x509
from cryptography.hazmat.backends import default_backend


def init():
    global found_domains
    global analyzed_domains
    found_domains = []
    analyzed_domains = []


def output(args, content, threads_safe):
    if content[0] in found_domains:
        return
    else:
        found_domains.append(content[0])

    print("\n[!] New Domain Found")
    if len(content) > 1:
        print(str(content[0]) + " " + "(" + str(content[1]) + ")")
    else:
        print(str(content[0]))

    if "-o" not in args:
        return
    else:
        file = args[args.index("-o") + 1]

    if threads_safe:
        lock = threading.Lock()
        lock.acquire()

    output_formats = {
        "d": str(content[0]),
        "i": str(content[1])
    }

    with open(file, "a") as f:
        if "-oF" in args:
            format = args[args.index("-oF") + 1]
            # replace variables that start with $ with the corresponding content
            for key, value in output_formats.items():
                format = format.replace("$" + key, value)
            f.write(format + "\n")
        else:
            f.write(str(content[0]) + "\n")

    if threads_safe:
        lock.release()


def validate_domain(domain):
    return re.match(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$", domain)


def check_wordlist(args):
    #check if the -w flag is present for wordlist
    if "-w" not in args:
        print("Usage: python main.py dns -d <domain> -e -w <wordlist>")
        sys.exit(1)

    wordlist = args[args.index("-w") + 1]
    #check if the wordlist file exists
    if not os.path.exists(wordlist):
        print("Wordlist not found")
        sys.exit(1)
    #check if the user has read permissions for the wordlist
    if not os.access(wordlist, os.R_OK):
        print("Permission denied")
        sys.exit(1)

    return wordlist


def check_domain_ip(domain):
    try:
        ip = socket.gethostbyname(domain)
    except socket.gaierror as e:
        return None
    return ip


def get_domains_from_input(args):
    # check if -i flag is present for input file
    if "-i" in args:
        file = args[args.index("-i") + 1]
        if not os.path.exists(file):
            print("Input file " + file + " does not exist")
            sys.exit(1)
        with open(file, "r") as f:
            domains = [line.strip() for line in f.readlines()]

    else:
        domains = []
    return [domain.strip() for domain in domains]


def get_certificate(domain):
    try:
        # Create a socket connection to the server
        context = ssl.create_default_context()
        context.load_verify_locations(certifi.where())

        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                # Get the certificate
                cert_bin = ssock.getpeercert(binary_form=True)
                print("Handshake succeded for " + domain)
                return cert_bin
    except:
        return None


def extract_san(cert_bin):
    if cert_bin is None:
        return []
    # Load the certificate
    cert = x509.load_der_x509_certificate(cert_bin, default_backend())
    # Extract SANs
    san_extension = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
    sans = san_extension.value
    return sans
