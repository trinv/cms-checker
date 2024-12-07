#!/usr/bin/python3

import os
import re
import json
import requests
import threading
import bs4
import time
import subprocess
import argparse
import socket
from queue import Queue
from pyfiglet import Figlet
from termcolor import colored
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

listData = []
timeout = 15
threads = 5

f = Figlet(font='slant')
print(colored(f.renderText('CMS Checker'), "red", attrs=['bold']))
print("===========================")
print("CMS Checker v3.1\nAuthor: Oways\nTwitter: https://twitter.com/0w4ys\nCMSs Included: Wordpress,Joomla,Drupal,Sharepoint\nNote: increase timeout if you have a slow internet connection")
print("===========================")

path = "result-%s" % time.strftime("%s-%m-%H_%d-%m-%Y")
outputPath = "%s" % path


def getServerIP(x):
    return socket.gethostbyname(x)


class ThreadedFetch(object):
    class FetchUrl(threading.Thread):
        def __init__(self, queue):
            threading.Thread.__init__(self)
            self.queue = queue

        def run(self):
            while not self.queue.empty():
                try:
                    url = self.queue.get()
                    title = ""
                    ip_port = ""
                    headers = {
                        'User-agent': 'Mozilla/5.0 (Windows; Intel 10.13; rv:52.0) Gecko/20100101 Firefox/52.0',
                        'X-Forwarded-For': '127.0.0.1'
                    }

                    response = requests.get(f'http://{url}/', timeout=timeout, headers=headers, verify=False,
                                            allow_redirects=True)
                    response.encoding = 'utf-8'  # Ensure response is handled as UTF-8
                    html = bs4.BeautifulSoup(response.text, "html.parser")
                    ip_ = getServerIP(url) if ":" not in url else url

                    if response.status_code == 200:
                        os.makedirs(outputPath, mode=0o755, exist_ok=True)
                        htmlpath = f"{outputPath}/{url.replace(':', '.')}.html"
                        with open(htmlpath, "w", encoding="utf-8") as f:
                            f.write(response.text)

                        title = html.title.text.strip() if html.title else ""
                        srv = response.headers.get('Server', "")

                        # CMS detection
                        cms = None
                        if "/sites/default/files/" in response.text:
                            cms = "Drupal"
                        elif "MicrosoftSharePointTeamServices" in response.headers:
                            cms = "SharePoint"
                        elif "wp-content" in response.text:
                            cms = "WordPress"
                        elif "com_content" in response.text:
                            cms = "Joomla"

                        cms_data = {
                            "Url": url,
                            "Title": title,
                            "IP": ip_,
                            "Status": response.status_code,
                            "Server": srv,
                            "CMS": cms or "",
                            "Version": "",
                            "Reference": ""
                        }

                        if cms:
                            print(colored(f"{url} => [{cms}] Server: {srv}", "green"))
                        else:
                            print(colored(f"{url} => Server: {srv}", "red"))

                        listData.append(cms_data)
                except Exception as e:
                    print(colored(f"Error processing {url}: {e}", "yellow"))
                finally:
                    self.queue.task_done()

    def __init__(self, urls=[], thread_count=5):
        self.queue = Queue(0)
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

        if listData:
            self.generate_output()

    @staticmethod
    def generate_output():
        print("\nGenerating the Output ...")
        html = '''
        <html>
        <head>
            <meta charset="UTF-8">
            <title>CMS Checker</title>
            <script src="../js/jquery-1.12.4.js"></script>
            <script src="../js/dataTables.bootstrap.min.js"></script>
            <script src="../js/jquery.dataTables.min.js"></script>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
            <link rel="stylesheet" href="../css/dataTables.bootstrap.min.css">
            <script>
                $(document).ready(function() {
                    $("#example").DataTable();
                });
            </script>
        </head>
        <body>
            <div id="example_wrapper" class="dataTables_wrapper form-inline dt-bootstrap">
                <table id="example" class="table table-striped table-bordered" cellspacing="0" width="100%">
                    <thead>
                        <th>#</th><th>Title</th><th>Url</th><th>IP</th><th>Status</th><th>CMS</th><th>Server</th><th>HTML Snapshot</th><th>Reference</th>
                    </thead>
                    <tbody>
        '''
        for i, data in enumerate(listData, start=1):  # Start numbering from 1
            html += f"""
            <tr>
                <td>{i}</td>
                <td>{data["Title"]}</td>
                <td><a href='http://{data["Url"]}' target='_blank'>{data["Url"]}</a></td>
                <td>{data["IP"]}</td>
                <td>{data["Status"]}</td>
                <td>{data["CMS"]}</td>
                <td>{data["Server"]}</td>
                <td><a href='./{data["Url"].replace(":", ".")}.html' target='_blank'>View</a></td>
                <td>{data["Reference"]}</td>
            </tr>
            """
        html += '''
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        '''
        outputHtml = f"{outputPath}/index.html"
        with open(outputHtml, "w", encoding="utf-8") as f:
            f.write(html)
        print(colored(f"Output path: {outputHtml}\n", "green"))


def main():
    parser = argparse.ArgumentParser(description="CMS Checker")
    parser.add_argument('-l', required=True, help="List of URLs", type=argparse.FileType('r'))
    parser.add_argument('-t', help="Number of threads [Default: 5]", type=int, default=5)
    args = parser.parse_args()

    urls = [line.strip() for line in args.l.readlines()]
    fetcher = ThreadedFetch(urls, args.t)
    fetcher.run()


if __name__ == "__main__":
    main()
