#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import json
import wget
import traceback
from urllib.parse import urlparse
from utils import reader
from paths import DUMP_HOME, DOWNLOADS
from libs.regex import img, video, executable
from libs.logger import logger
from collections import Counter

# suffix = list()
# for url in reader(os.path.join(DUMP_HOME, 'file_urls.txt')):
#     suffix.append(urlparse(url).path.split('.')[-1].lower())
#
# counter = Counter(suffix)
# print(json.dumps(dict(counter.most_common()), indent=4))
#

for url in reader(os.path.join(DUMP_HOME, 'file_urls.txt')):
    path = urlparse(url).path
    if img.match(path) or video.match(path) or executable.match(path):
        continue
    try:
        filename = wget.download(url, out=DOWNLOADS)
        logger.info('%s\n>> %s' % (url, filename))
    except:
        # UnicodeError: encoding with 'idna' codec failed (UnicodeError: label empty or too long)
        logger.error(traceback.format_exc())


