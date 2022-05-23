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
import re
import os
import json
import shutil
import rarfile
from py7zr import pack_7zarchive, unpack_7zarchive
from docx import Document
import pandas as pd
from id_validator import validator
from urllib.parse import urlparse
from utils import tree, tree2list
from utils import reader, traverse
from modules.btbu.util import find_idcard
from paths import DOWNLOADS, DUMP_HOME
from libs.logger import logger


def download():
    n_failed = n_success = 0
    suffix = list()
    for url in reader(os.path.join(DUMP_HOME, 'file_urls.txt')):
        path = urlparse(url).path
        # 默认不下载图片和可执行文件
        if img.match(path) or video.match(path) or executable.match(path):
            continue
        try:
            filename = wget.download(url, out=DOWNLOADS)
            n_success += 1
            suffix.append(path.split('.')[-1].lower())
            logger.info('%s\n>> %s' % (url, filename))
        except:
            # UnicodeError: encoding with 'idna' codec failed (UnicodeError: label empty or too long)
            n_failed += 1
            logger.error(traceback.format_exc())
    # 统计文件类型数量
    counter = Counter(suffix)
    print('文档和压缩包数量:', sum(counter.values()), '\n下载成功数量:', n_success, '\n下载失败数量:', n_failed)
    print('文件类型分布:\n', json.dumps(dict(counter.most_common()), indent=4))


if __name__ == '__main__':
    # load2stats(DOWNLOADS)
    download()

