#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import tika
from tika import parser

home = '/home/ljm/docs/'
for filename in os.listdir(home):
    filepath = os.path.join(home, filename)
    print(filepath)
    parsed = parser.from_file(filepath)
    print('>>', parsed["content"])
