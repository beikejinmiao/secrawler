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


def url_filetype():
    valid_file_count = 0
    suffix = list()
    for url in reader(os.path.join(DUMP_HOME, 'file_urls.txt')):
        path = urlparse(url).path
        if not (img.match(path) or video.match(path) or executable.match(path)):
            valid_file_count += 1
        suffix.append(path.split('.')[-1].lower())

    counter = Counter(suffix)
    print('文件总数量:', sum(counter.values()), '\n文档和压缩包数量:', valid_file_count)
    print('文件类型分布:\n', json.dumps(dict(counter.most_common()), indent=4))


def download():
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
    # 统计文件类型数量
    url_filetype()


def _safe_int(item):
    try:
        i = int(item)
    except:
        i = 0
    return i


def load2stats(path):
    stats = tree()
    files = traverse(path)
    for filepath in files:
        filename = os.path.basename(filepath)
        suffix = filename.split('.')[-1].lower()
        try:
            if re.match(r'.*\.(zip|7z|tar|tar\.bz2|tar\.gz|tar\.xz|tbz2|tgz|txz)$', filepath, re.I):
                dest_dir = filepath + '.unpack'
                # shutil.ReadError: xxx.zip is not a zip file
                shutil.unpack_archive(filepath, dest_dir)
            elif filename.endswith('.rar'):
                # TODO: rarfile.RarCannotExec: Cannot find working tool
                rarfile.UNRAR_TOOL = r"C:\OptSoft\unrar\UnRAR.exe"
                rar = rarfile.RarFile(filepath)
                dest_dir = filepath + '.unpack'
                with rar as rf:
                    rf.extractall(dest_dir)
            elif re.match(r'.*\.(txt|csv|xml|json)$', filepath, re.I):
                reader(filepath)
            elif re.match(r'.*\.doc[x]?$', filepath, re.I):
                logger.info("Load: '%s'" % filepath)
                # docx.opc.exceptions.PackageNotFoundError: Package not found at ''
                doc = Document(filepath)
            elif re.match(r'.*\.xls[x]?$', filepath, re.I):
                logger.info("Load: '%s'" % filepath)
                # ValueError: Excel file format cannot be determined, you must specify an engine manually.
                xls = pd.read_excel(filepath, sheet_name=None)
            else:
                continue
            stats[suffix]['success'] = _safe_int(stats[suffix]['success']) + 1
        except Exception as e:
            logger.error(e)
            stats[suffix]['failed'] = _safe_int(stats[suffix]['failed']) + 1
    logger.info(json.dumps(dict(stats)))


if __name__ == '__main__':
    # load2stats(DOWNLOADS)
    download()

