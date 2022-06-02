#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import hashlib
from id_validator import validator
from paths import DOWNLOADS
from utils import traverse

# 大陆居民身份证/港澳居民居住证/台湾居民居住证18位
# 不提取15位大陆居民身份证
idcard_pattern = re.compile(r'\b\d{17}(?:\d|X)\b', re.I)


def check_idcard(idcard):
    return validator.is_valid(idcard)


def find_idcard(text):
    # return [x for x in idcard_pattern.findall(text) if check_idcard(x)]
    return [x for x in idcard_pattern.findall(text) if x]


def downloaded_md5():
    md5_dict = dict()
    for filepath in traverse(DOWNLOADS):
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        md5_dict[hash_md5.hexdigest()] = filepath
    return md5_dict


