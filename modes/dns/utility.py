import threading
import re
import sys
import os
import socket
import modes.dns.dns_main as dns_main
import dns.resolver


def output(args, content, threads_safe):
    
    print(str(content[0]) + " " + "(" + str(content[1]) + ")")

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
            #replace variables that start with $ with the corresponding content
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
    except socket.gaierror:
        #print("Invalid domain")
        return None
    return ip


