#!/usr/bin/env python
import sys
import os

DNS = "dns"

# Check which mode is specified
if len(sys.argv) < 2:
    print("Usage: python main.py <mode> <args>")
    sys.exit(1)

mode = sys.argv[1]

# Check if the -o flag is present for output file
if "-o" in sys.argv:
    file = sys.argv[sys.argv.index("-o") + 1]

    # Check if file exists
    if os.path.exists(file):
        if not os.access(file, os.W_OK):
            print("Cannot open output file " + file + ", permission denied")
            sys.exit(1)
        # empty the file
        open(file, "w").close()
    else:
        directory = os.path.dirname(file)

        # check if the path is relative
        if not os.path.isabs(directory):
            directory = os.path.join(os.getcwd(), directory)

# check if the -mT flag is present for max thread count
if "-mT" in sys.argv:
    max_threads = int(sys.argv[sys.argv.index("-mT") + 1])
    print("\nRunning with " + str(max_threads) + " threads")
else:
    max_threads = None

# switch to the specified mode
if mode == DNS:
    from modes.dns import main as dns
    dns.main(sys.argv[2:], max_threads)
