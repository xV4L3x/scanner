#!/usr/bin/env python
import sys
import os

DNS = "dns"

#check which mode is specified
if (len(sys.argv) < 2):
    print("Usage: python main.py <mode> <args>")
    sys.exit(1)

mode = sys.argv[1]
sys.path.insert(0, 'modes')


#check if the -o flag is present for output file
if "-o" in sys.argv:
    file = sys.argv[sys.argv.index("-o") + 1]

    #check if file exists
    if os.path.exists(file):
        if not os.access(file, os.W_OK):
            print("Cannot open output file "+ file + ", permission denied")
            sys.exit(1)
        #empty the file
        open(file, "w").close()
    else:
        directory = os.path.dirname(file)

        #check if the path is relative
        if not os.path.isabs(directory):
            directory = os.path.join(os.getcwd(), directory)
        
        #TODO: check if the user has write permissions for the directory

#check if the -mT flag is present for max thread count
if "-mT" in sys.argv:
    max_threads = int(sys.argv[sys.argv.index("-mT") + 1])
    print("\nRunning with " + str(max_threads) + " threads")
else:
    max_threads = None

#switch to the specified mode
if mode == DNS:
    sys.path.insert(0, 'modes/'+ DNS)
    import dns_main as dns
    dns.main(sys.argv[2:], max_threads)