#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import os
import shutil
from py7zr import pack_7zarchive, unpack_7zarchive
from docx import Document
import pandas as pd
from utils import tree
from utils import reader, traverse
from modules.btbu.util import find_idcard

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
        if re.match(r'.*\.(txt|csv|xml|json)$', filepath, re.I):
            for line in reader(filepath):
                candidates.extend(find_idcard(line))
        elif re.match(r'.*\.doc[x]?$', filepath, re.I):
            print("Load: '%s'" % filepath)
            doc = Document(filepath)
            for p in doc.paragraphs:
                candidates.extend(find_idcard(p.text))
        elif re.match(r'.*\.xls[x]?$', filepath, re.I):
            print("Load: '%s'" % filepath)
            xls = pd.read_excel(filepath, sheet_name=None)
            for name, sheet in xls.items():
                for index, row in sheet.iterrows():
                    for value in row:
                        candidates.extend(find_idcard(value))

        if len(candidates) > 0:
            results[filename] = list(set(candidates))
    return results


def unarchive(path):
    files = traverse(path)
    results = tree()
    for filepath in files:
        filename = os.path.basename(filepath)
        if re.match(r'.*\.(zip|7z|tar|tar\.bz2|tar\.gz|tar\.xz|tbz2|tgz|txz)$', filepath, re.I):
            dest_dir = filepath + '.unpack'
            shutil.unpack_archive(filepath, dest_dir)
            ret = load2find(dest_dir)
            if len(ret) > 0:
                results[filename] = ret
        elif filename.endswith('.rar'):
            pass
        else:
            ret = load2find(filepath)
            if len(ret) > 0:
                results[''][filename] = ret[filename]
    return results


if __name__ == '__main__':
    import json
    print(json.dumps(unarchive(os.path.join(os.path.dirname(__file__), 'test')), indent=4))

