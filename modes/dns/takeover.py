import os
import sys
import utility
import re
import requests
import threading

services = {
    "AWS/S3": {"error": r"The specified bucket does not exist"},
    "Bitbucket": {"error": r"Repository not found"},
    "Github": {
        "error": r"There isn\\\'t a Github Pages site here\.|a Github Pages site here"
    },
    "Shopify": {"error": r"Sorry\, this shop is currently unavailable\."},
    "Fastly": {"error": r"Fastly error\: unknown domain\:"},
    "Ghost": {
        "error": r"The thing you were looking for is no longer here\, or never was"
    },
    "Heroku": {
        "error": r"no-such-app.html|<title>no such app</title>|herokucdn.com/error-pages/no-such-app.html|No such app"
    },
    "Pantheon": {
        "error": r"The gods are wise, but do not know of the site which you seek|404 error unknown site"
    },
    "Tumbler": {
        "error": r"Whatever you were looking for doesn\\\'t currently exist at this address."
    },
    "Wordpress": {"error": r"Do you want to register"},
    "TeamWork": {"error": r"Oops - We didn\'t find your site."},
    "Helpjuice": {"error": r"We could not find what you\'re looking for."},
    "Helpscout": {"error": r"No settings were found for this company:"},
    "Cargo": {"error": r"<title>404 &mdash; File not found</title>"},
    "Uservoice": {"error": r"This UserVoice subdomain is currently available"},
    "Surge.sh": {"error": r"project not found"},
    "Intercom": {
        "error": r"This page is reserved for artistic dogs\.|Uh oh\. That page doesn\'t exist</h1>"
    },
    "Webflow": {
        "error": r"<p class=\"description\">The page you are looking for doesn\'t exist or has been \
moved.</p>|The page you are looking for doesn\'t exist or has been moved"
    },
    "Kajabi": {"error": r"<h1>The page you were looking for doesn\'t exist.</h1>"},
    "Thinkific": {
        "error": r"You may have mistyped the address or the page may have moved."
    },
    "Tave": {"error": r"<h1>Error 404: Page Not Found</h1>"},
    "Wishpond": {"error": r"<h1>https://www.wishpond.com/404?campaign=true"},
    "Aftership": {
        "error": r"Oops.</h2><p class=\"text-muted text-tight\">The page you\'re looking for doesn\'t exist."
    },
    "Aha": {"error": r"There is no portal here \.\.\. sending you back to Aha!"},
    "Tictail": {
        "error": r"to target URL: <a href=\"https://tictail.com|Start selling on Tictail."
    },
    "Brightcove": {"error": r"<p class=\"bc-gallery-error-code\">Error Code: 404</p>"},
    "Bigcartel": {"error": r"<h1>Oops! We couldn&#8217;t find that page.</h1>"},
    "ActiveCampaign": {"error": r"alt=\"LIGHTTPD - fly light.\""},
    "Campaignmonitor": {
        "error": r"Double check the URL or <a href=\"mailto:help@createsend.com|Trying to access your account"
    },
    "Acquia": {
        "error": r"The site you are looking for could not be found.|If you are an Acquia Cloud \
customer and expect to see your site at this address|Web Site Not Found"
    },
    "Proposify": {
        "error": r"If you need immediate assistance, please contact <a href=\"mailto:support@proposify.biz"
    },
    "Simplebooklet": {
        "error": r"We can\'t find this <a href=\"https://simplebooklet.com"
    },
    "GetResponse": {
        "error": r"With GetResponse Landing Pages, lead generation has never been easier"
    },
    "Vend": {"error": r"Looks like you\'ve traveled too far into cyberspace."},
    "Jetbrains": {"error": r"is not a registered InCloud YouTrack."},
    "Smartling": {"error": r"Domain is not configured"},
    "Pingdom": {"error": r"pingdom|Sorry, couldn\'t find the status page"},
    "Tilda": {"error": r"Domain has been assigned|Please renew your subscription"},
    "Surveygizmo": {"error": r"data-html-name"},
    "Mashery": {"error": r"Unrecognized domain <strong>|Unrecognized domain"},
    "Divio": {"error": r"Application not responding"},
    "feedpress": {"error": r"The feed has not been found."},
    "Readme.io": {"error": r"Project doesnt exist... yet!"},
    "statuspage": {"error": r"You are being <a href=\'https>"},
    "zendesk": {"error": r"Help Center Closed"},
    "worksites.net": {"error": r"Hello! Sorry, but the webs>"},
    "Agile CRM": {"error": r"this page is no longer available"},
    "Anima": {
        "error": r"try refreshing in a minute|this is your website and you've just created it"
    },
    "Fly.io": {"error": r"404 Not Found"},
    "Gemfury": {"error": r"This page could not be found"},
    "HatenaBlog": {"error": r"404 Blog is not found"},
    "Kinsta": {"error": r"No Site For Domain"},
    "LaunchRock": {
        "error": r"It looks like you may have taken a wrong turn somewhere|worry...it happens to all of us"
    },
    "Ngrok": {"error": r"ngrok.io not found"},
    "SmartJobBoard": {
        "error": r"This job board website is either expired or its domain name is invalid"
    },
    "Strikingly": {"error": r"page not found"},
    "Tumblr": {
        "error": r"Whatever you were looking for doesn\'t currently exist at this address"
    },
    "Uberflip": {
        "error": r"hub domain\, The URL you\'ve accessed does not provide a hub"
    },
    "Unbounce": {"error": r"The requested URL was not found on this server"},
    "Uptimerobot": {"error": r"page not found"},
}


def output(domain, possible_takeover, service=None):
    if possible_takeover:
        print("[" + domain + "]" + " Possible takeover detected! (service:" + service + ")")
    else:
        print("[" + domain + "]" + " No possible takeover detected")


def check_takeover(section):

    #send request to each domain
    for domain in section:
        domain = domain.strip()

        if utility.validate_domain(domain):

            try:
                url = "http://" + domain
                response = requests.get(url, timeout=20)
                status = response.status_code

                for service in services:
                    error = services[service]["error"]
                    if (re.findall(error, response.text, re.I)):
                        output(domain, True, service)
                        break
                
                
                url = "https://" + domain
                response = requests.get(url, timeout=20)

                for service in services:
                    error = services[service]["error"]
                    if (re.findall(error, response.text, re.I)):
                        output(domain, True, service)
                        break
            except requests.exceptions.RequestException as e:
                output(domain, False)
                continue


            

            output(domain, False)


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


    #split domain list into threads
    thread_list = []
    sectionlen = len(domains) // threads

    for i in range(threads):
        if (i == threads - 1):
            section = domains[i * sectionlen:]
        else:
            section = domains[i * sectionlen:(i + 1) * sectionlen]

        from numpy import asarray
        section = asarray(section)

        t = threading.Thread(target=check_takeover, args=(section,))
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

