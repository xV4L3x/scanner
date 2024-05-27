import sys
import utility
import os
from collections import defaultdict
import pandas as pd
import concurrent.futures
import dns.resolver


def output(args, line):
    if "-o" in args:
        file = args[args.index("-o") + 1]
        with open(file, "a") as f:
            f.write(line + "\n")

    print(line)
    

def main(args, threads):
    #check if -d flag is present for domain
    if "-d" not in args:
        print("Usage: python main.py dns hierarchy -d <domain> -i <input_file>")
        sys.exit(1)

    domain = args[args.index("-d") + 1]

    #check if the domain is valid with regex
    if not utility.validate_domain(domain):
        print("Invalid domain")
        sys.exit(1)

    #check if -i flag is present for input file
    if "-i" in args:
        file = args[args.index("-i") + 1]
        if not os.path.exists(file):
            print("Input file " + file + " does not exist")
            sys.exit(1)
        with open(file, "r") as f:
            subdomains = f.readlines()
    else:
        print("Usage: python main.py dns hierarchy -d <domain> -i <input_file>")
        sys.exit(1)

    valid_subdomains = []
    for subdomain in subdomains:
        subdomain = subdomain.strip()
        if not utility.validate_domain(subdomain):
            continue
        if not subdomain.endswith(domain):
            continue
        if subdomain == domain:
            continue
        valid_subdomains.append(subdomain)

    subdomains = valid_subdomains

    #class to store the subdomains in a tree structure
    class domain_node:
        def append_child(self, domain):
            self.children.append(domain)

        def maltego(self):

            def manage_record_types(domain):
                record_types = ["A", "CNAME"]


                #print(domain)
                for record_type in record_types:
                    result = os.popen("dig " + domain + " " + record_type + " +short").read()
                    if len(result.split("\n")) == 2:
                        return (record_type, result.split("\n")[0])
                
                print("No record found for " + domain)
                return (None, None)        
            
            ips = {}
            cnames = {}
            types = {}
            subdomains.append(domain)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(manage_record_types, subdomains)
                for subdomain, (type, target) in zip(subdomains, results):
                    if type == "A":
                        ips[subdomain] = target
                    if type == "CNAME":
                        cnames[subdomain] = target[:-1]
                    types[subdomain] = type
            
            #create an empty dataframe
            df = pd.DataFrame(columns=["A-Record", "CNAME-Record", "IPV4-Address", "Child-Record"])
            def fill_dataframe(node):

                

                if len(node.children) == 0 and types[node.domain] == "A":
                    df.loc[len(df.index)] = [
                        node.domain, 
                        None, 
                        ips[node.domain],
                        None
                    ]

                if types[node.domain] == "CNAME":
                    df.loc[len(df.index)] = [
                        None, 
                        node.domain, 
                        None,
                        cnames[node.domain]
                    ]

               


                for child in node.children:

                    
                    
                    if types[child.domain] == "CNAME":
                        
                        if types[node.domain] == "A":
                            df.loc[len(df.index)] = [
                                node.domain, 
                                None, 
                                ips[node.domain],
                                None
                            ]

                        fill_dataframe(child)
                        continue

                    #Create A record
                    df.loc[len(df.index)] = [
                        None, 
                        None, 
                        ips[node.domain],
                        child.domain
                    ]

                    column = types[node.domain] + "-Record" 
                    df.loc[len(df.index) - 1][column] = node.domain

                    fill_dataframe(child)



            fill_dataframe(self)

            #REMOVE ALL ROWS WHERE CHILD_RECORD IS A CNAME
            for row in range(len(df.index)):
                if df.loc[row]["Child-Record"] in cnames:
                    df.loc[row]["Child-Record"] = None



            print(df)

            #export the dataframe to a csv file
            if "-o" in args:
                file = args[args.index("-o") + 1]
                df.to_csv(file, index=False)

            
        def print_tree(self, level):
            ip = None
            if "--show-ip" in args:
                ip = utility.check_domain_ip(self.domain)

            record_type = None
            if "--show-record-type" in args:
                pass

            line = (("   " * (level - 1)) if level > 1 else "") + ("" if level == 0 else "\\__") + self.domain + ("" if record_type is None else " " + record_type + " record") + ("" if ip is None else " (" + ip + ")")
            output(args, line)
            for child in self.children:
                child.print_tree(level + 1)

        def search_node(self, domain):
            if self.domain == domain:
                return self
            for child in self.children:
                result = child.search_node(domain)
                if result:
                    return result
            return None

        def __init__(self, domain, parent):
            self.domain = domain
            self.children = []
            self.parent = parent

    #create the root node
    root = domain_node(domain, None)
    maxlen = max([len(subdomain.split(".")) for subdomain in subdomains])

    for l in range(len(domain.split(".")) + 1, maxlen + 1):
        count = 0
        for subdomain in subdomains:
            if (len(subdomain.split(".")) == l):
                #check if subdomain is already in the tree
                if root.search_node(subdomain) is not None:
                    continue
                parent = root.search_node(".".join(subdomain.split(".")[1:]))
                if parent is not None:
                    parent.append_child(domain_node(subdomain, parent))
                    count += 1
                else:
                    root.append_child(domain_node(subdomain, root))
                    count += 1
    

    root.maltego()
    #root.print_tree(0)



        


    
        


