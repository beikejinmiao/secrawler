#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re

idcard_pattern = re.compile(r'\b\d{17}(?:\d|X)\b', re.I)


def check_idcard(idcard):
    return True


def find_idcard(text):
    return [x for x in idcard_pattern.findall(text) if check_idcard(x)]


