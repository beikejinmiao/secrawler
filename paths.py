#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os

# 工作目录
MAIN_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__)))

# 工程名
WORK_NAME = MAIN_HOME.split(os.sep)[-1].lower()    # secrawler


DUMP_HOME = os.path.join(MAIN_HOME, 'zdump')
if not os.path.exists(DUMP_HOME):
    os.mkdir(DUMP_HOME)

