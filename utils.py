#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
from datetime import datetime
from collections import defaultdict


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

