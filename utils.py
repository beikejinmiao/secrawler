#!/usr/bin/env python
# -*- coding:utf-8 -*-
import io
import os
import json
from datetime import datetime
from collections import defaultdict
from libs.logger import logger


def tree():
    return defaultdict(tree)


def tree2list(tr):
    lists = list()

    def _tree2list(d, ls):
        for k, v in d.items():
            ls.append(k)
            if isinstance(v, dict):
                _tree2list(v, ls)
            else:
                lists.append(ls + [v])
            ls.pop(-1)

    _tree2list(tr, list())
    return lists


def cur_date(msec=False):
    if msec is True:
        return datetime.now().isoformat(timespec='milliseconds')
    return datetime.now().isoformat(timespec='seconds')


def writer(path, texts, method="w", encoding='utf-8'):
    with open(path, method, encoding=encoding) as fout:
        if isinstance(texts, str):
            fout.write(texts)
        elif isinstance(texts, dict):
            json.dump(texts, fout, indent=4)
        else:
            fout.write('\n'.join(texts))


def reader(path, encoding='utf-8', strip="\r\n ", skip_blank=True, raisexp=False):
    with io.open(path, encoding=encoding) as fopen:
        logger.info("Load: '%s'" % path)
        while True:
            try:
                line = fopen.readline()
            except Exception as e:
                if raisexp:
                    raise e
                # UnicodeDecodeError: 'utf8' codec can't decode byte 0xfb in position 17: invalid start byte
                continue
            if not line:
                break
            # check the line whether is blank or not
            line = line.strip(strip)
            if skip_blank and not line:
                continue
            yield line


def traverse(top, contains=None):
    files = list()
    if not os.path.exists(top):
        logger.warn("'%s' is not existed" % top)
        return files
    if os.path.isfile(top):
        files.append(top)
        return files

    for root, dirs, filenames in os.walk(top):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            if contains and contains not in filename:
                continue

            files.append(file_path)
    print("File total count: %d" % len(files))
    return files

