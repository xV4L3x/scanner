#!/usr/bin/env python3
import sys
import socket
import enumeration
import takeover
import alive
import hierarchy


ENUMERATION = "enum"
TAKEOVER = "takeover"
ALIVE = "alive"
HIERARCHY = "hierarchy"


def main(args, threads):

    if len(args) < 1:
        print("Usage: python main.py dns <mode> <args>")
        sys.exit(1)

    if args[0] == ENUMERATION:
        enumeration.main(args[1:], threads)
    elif args[0] == TAKEOVER:
        takeover.main(args[1:], threads)
    elif args[0] == ALIVE:
        alive.main(args[1:], threads)
    elif args[0] == HIERARCHY:
        hierarchy.main(args[1:], threads)
        

   




        


    