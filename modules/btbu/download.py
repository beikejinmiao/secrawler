#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import json
import wget
from urllib.parse import urlparse
from utils import reader
from paths import DUMP_HOME, DOWNLOADS
from libs.regex import img, video, executable
from collections import Counter

# suffix = list()
# for url in reader(os.path.join(DUMP_HOME, 'file_urls.20220426.txt')):
#     suffix.append(urlparse(url).path.split('.')[-1].lower())
#
# counter = Counter(suffix)
# print(json.dumps(dict(counter.most_common()), indent=4))
#

for url in reader(os.path.join(DUMP_HOME, 'file_urls.20220426.txt')):
    path = urlparse(url).path
    if img.match(path) or video.match(path) or executable.match(path):
        continue
    filename = wget.download(url, out=DOWNLOADS)
    print(url, '\n>>', filename)
