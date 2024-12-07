#!/usr/bin/python3

import sys
import os
import re
import json
import requests
import threading
import time
import subprocess
import argparse
import socket
from queue import Queue
from bs4 import BeautifulSoup
from termcolor import colored
from importlib import reload
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Globals
listData = []
timeout = 15
threads = 5

# ASCII Art for Script Banner
print(colored("CMS Checker", "red", attrs=["bold"]))
print("=" * 30)
print(
    "CMS Checker v4.0\nAuthor: Oways\nTwitter: https://twitter.com/0w4ys\n"
    "CMSs Included: Wordpress, Joomla, Drupal, Sharepoint\n"
    "Note: Increase timeout if you have a slow internet connection"
)
print("=" * 30)

# Output directory setup
path = f"result-{time.strftime('%s-%m-%H_%d-%m-%Y')}"
outputPath = path

# Get IP from hostname
def getServerIP(x):
    try:
        return socket.gethostbyname(x)
    except socket.error as e:
        print(colored(f"Error resolving IP for {x}: {e}", "yellow"))
        return "Unknown"


# Threaded CMS Fetching Class
class ThreadedFetch:
    class FetchUrl(threading.Thread):
        def __init__(self, queue):
            threading.Thread.__init__(self)
            self.queue = queue

        def run(self):
            while not self.queue.empty():
                url = self.queue.get()
                try:
                    self.process_url(url)
                except Exception as e:
                    print(colored(f"Error processing {url}: {e}", "yellow"))
                finally:
                    self.queue.task_done()

        def process_url(self, url):
            title = ""
            ip_ = getServerIP(url)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "X-Forwarded-For": "127.0.0.1",
            }
            try:
                response = requests.get(
                    f"http://{url}/", timeout=timeout, headers=headers, verify=False, allow_redirects=True
                )
            except requests.RequestException as e:
                print(colored(f"Request error for {url}: {e}", "red"))
                return

            html = BeautifulSoup(response.text, "html.parser")
            title = html.title.text.strip() if html.title else "No Title"
            srv = response.headers.get("Server", "Unknown Server")
            
            cms_detected = False
            # CMS Detection Logic
            if "/sites/default/files/" in response.text:
                cms_detected = True
                cms = "Drupal"
            elif "MicrosoftSharePointTeamServices" in response.headers:
                cms_detected = True
                cms = "SharePoint"
            elif "wp-content" in response.text:
                cms_detected = True
                cms = "WordPress"
            elif "com_content" in response.text:
                cms_detected = True
                cms = "Joomla"
            else:
                cms = "Unknown"

            if cms_detected:
                print(colored(f"{url} => [{cms}] Server: {srv}", "green"))
            else:
                print(colored(f"{url} => Server: {srv}", "yellow"))

            # Save to list
            listData.append(
                {
                    "Url": url,
                    "Title": title,
                    "IP": ip_,
                    "Status": response.status_code,
                    "Server": srv,
                    "CMS": cms,
                    "Version": "",
                    "Reference": "",
                }
            )
            # Save raw HTML snapshot
            if not os.path.exists(outputPath):
                os.makedirs(outputPath, mode=0o755, exist_ok=True)
            with open(f"{outputPath}/{url.replace(':', '.')}.html", "w", encoding="utf-8") as f:
                f.write(response.text)

    def __init__(self, urls, thread_count=5):
        self.queue = Queue()
        self.threads = []
        self.thread_count = thread_count
        for url in urls:
            self.queue.put(url)

    def run(self):
        for _ in range(self.thread_count):
            thread = ThreadedFetch.FetchUrl(self.queue)
            thread.start()
            self.threads.append(thread)
        self.queue.join()


# Argument Parser
def parse_args():
    parser = argparse.ArgumentParser(description="CMS Checker")
    parser.add_argument(
        "-l", "--list", required=True, help="Path to the list of URLs (one per line)", type=argparse.FileType("r")
    )
    parser.add_argument(
        "-t", "--threads", help="Number of threads [Default: 5]", type=int, default=5
    )
    return parser.parse_args()


def main():
    args = parse_args()
    urls = [line.strip() for line in args.list.readlines() if line.strip()]
    thread_count = min(args.threads, 20)

    print("\nStarting CMS Checker...\n")
    fetcher = ThreadedFetch(urls, thread_count)
    fetcher.run()

    # Generate HTML Report
    if listData:
        print("\nGenerating Output...")
        output_file = f"{outputPath}/index.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("<html><head><title>CMS Checker Results</title></head><body>")
            f.write("<h1>CMS Checker Results</h1><table border='1'>")
            f.write(
                "<tr><th>#</th><th>Title</th><th>URL</th><th>IP</th><th>Status</th><th>CMS</th><th>Server</th></tr>"
            )
            for idx, data in enumerate(listData):
                f.write(
                    f"<tr><td>{idx}</td><td>{data['Title']}</td><td>{data['Url']}</td>"
                    f"<td>{data['IP']}</td><td>{data['Status']}</td><td>{data['CMS']}</td>"
                    f"<td>{data['Server']}</td></tr>"
                )
            f.write("</table></body></html>")
        print(colored(f"Output saved to {output_file}", "green"))


if __name__ == "__main__":
    main()
