#!/bin/python3

# Copyright (C) 2023 William Welna (wwelna@occultusterra.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Run to keep up to date:
#   for x in */;do cd $x && echo "Updating $x" && git pull && cd ..;done

import requests
import json
import re

class fetchy:

    def __init__(self, UserAgent="Mozilla/5.0 (LOL)"):
        self.UserAgent = UserAgent
        self.headers = {'user-agent': self.UserAgent}
        self.linkRE = re.compile("<([a-zA-Z0-9\&\/:\?\=\.\_\-]+)>; rel=\"([a-z]+)\"")
    
    def fetch(self, url):
        r = requests.get(url, headers=self.headers)
        if r.status_code == 200:
            ret = {'json':json.loads(r.text)}
            if 'link' in r.headers:
                link = []
                for (link_url, link_rel) in self.linkRE.findall(r.headers['link']):
                    link.append({link_rel:link_url})
                ret['link'] = link
            return ret
        else:
            print(url)
            print(r.headers)
            print(r.text)
            return None

class IterRepos:
    
    def __init__(self, user, type='user'):
        self.user = user
        self.type = type
        self.is_more = True
        self.first_run = True
        self.link = []
        self.results = []
        self.client = fetchy()
    
    def __iter__(self):
        self._getmore()
        return self
    
    def __next__(self):
        if len(self.results) > 0:
            return self.results.pop(0)
        else: 
            self._getmore()
            if len(self.results) > 0:
                return self.results.pop(0)
            else: raise StopIteration

    def _getmore(self):
        if self.is_more == True:
            if self.first_run == True:
                r = self.client.fetch(f"https://api.github.com/{self.type}/{self.user}/repos?per_page=100")
                self.results = r['json']
                if 'link' in r: self.link = r['link']
                self.first_run = False
            else:
                for l in self.link:
                    if 'next' in l:
                        r = self.client.fetch(l['next'])
                        self.results = r['json']
                        self.link = r['link']

if __name__ == "__main__":
    import argparse
    import subprocess
    
    parser = argparse.ArgumentParser(description='Mirror Github Repos of a User/Group')
    parser.add_argument('--type', help="Specify if it's a 'user' or 'orgs' to mirror", default='user')
    parser.add_argument('name', help="Name of Organization or User to mirror")
    args = parser.parse_args()
    
    repos = []
    for x in IterRepos(args.name, args.type):
        repos.append(x)
    
    print(f"-> Found {len(repos)} repos for {args.type}/{args.name}\n")

    for x in repos:
        print(f"-> Mirroring {x['html_url']}")
        p = subprocess.Popen(['git', 'clone', x['html_url']])
        p.wait()