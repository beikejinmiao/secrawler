#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
from id_validator import validator


# 大陆居民身份证/港澳居民居住证/台湾居民居住证18位
# 不提取15位大陆居民身份证
idcard_pattern = re.compile(r'\b\d{17}(?:\d|X)\b', re.I)


def check_idcard(idcard):
    return validator.is_valid(idcard)


def find_idcard(text):
    # return [x for x in idcard_pattern.findall(text) if check_idcard(x)]
    return [x for x in idcard_pattern.findall(text) if x]


