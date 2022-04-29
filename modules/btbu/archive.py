#!/usr/bin/env python
# -*- coding:utf-8 -*-
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

# https://bbs.huaweicloud.com/blogs/180864
# register file format at first.
shutil.register_archive_format('7zip',
                               pack_7zarchive,
                               description='7zip archive')
shutil.register_unpack_format('7zip',
                              ['.7z'],
                              unpack_7zarchive,
                              description='7zip archive')


def load2find(path):
    files = traverse(path)
    results = dict()
    for filepath in files:
        filename = os.path.basename(filepath)
        candidates = list()
        try:
            if re.match(r'.*\.(txt|csv|xml|json)$', filepath, re.I):
                for line in reader(filepath):
                    candidates.extend(find_idcard(line))
            elif re.match(r'.*\.doc[x]?$', filepath, re.I):
                logger.info("Load: '%s'" % filepath)
                # docx.opc.exceptions.PackageNotFoundError: Package not found at ''
                doc = Document(filepath)
                for p in doc.paragraphs:
                    candidates.extend(find_idcard(p.text))
            elif re.match(r'.*\.xls[x]?$', filepath, re.I):
                logger.info("Load: '%s'" % filepath)
                # ValueError: Excel file format cannot be determined, you must specify an engine manually.
                xls = pd.read_excel(filepath, sheet_name=None)
                for name, sheet in xls.items():
                    for index, row in sheet.iterrows():
                        for value in row:
                            candidates.extend(find_idcard(str(value)))
        except Exception as e:
            logger.error(e)
        if len(candidates) > 0:
            results[filename] = list(set(candidates))
    return results


def unarchive(path):
    files = traverse(path)
    results = tree()
    for filepath in files:
        filename = os.path.basename(filepath)
        try:
            dest_dir = ''
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
            #
            if dest_dir:
                ret = load2find(dest_dir)
                pkg_name = filename
                if len(ret) > 0:
                    results[pkg_name] = ret
            else:
                ret = load2find(filepath)
                pkg_name = ''
                if len(ret) > 0:
                    results[pkg_name][filename] = ret[filename]
        except Exception as e:
            logger.error(e)
    return results


def dump2csv(infos):
    df = pd.DataFrame(tree2list(infos), columns=['archive', 'filename', 'idcard'])
    df = df.assign(idcard=df["idcard"]).explode("idcard").reset_index(drop=True)
    df['is_valid'] = df['idcard'].map(lambda x: 1 if validator.is_valid(x) else 0)
    with open(os.path.join(DUMP_HOME, 'file_urls.json')) as fopen:
        file_urls = json.load(fopen)
    fname2url = dict()
    for file_url in file_urls:
        filename = os.path.basename(urlparse(file_url).path)
        fname2url[filename] = (file_urls[file_url], file_url)
    csv = list()
    for index, row in df.iterrows():
        filename = row['archive'] if row['archive'] else row['filename']
        url, file_url = '', ''
        if filename in fname2url:
            url, file_url = fname2url[filename]
        csv.append(dict(zip(['url', 'file_url', 'archive', 'filename', 'idcard', 'is_valid'],
                            [url, file_url, row['archive'], row['filename'], row['idcard'], row['is_valid']])))
    pd.DataFrame(csv).to_csv(os.path.join(DUMP_HOME, 'file_results.csv'))


if __name__ == '__main__':
    infos = unarchive(DOWNLOADS)
    print(json.dumps(infos))
    dump2csv(infos)




