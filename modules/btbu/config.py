#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import platform
from paths import MAIN_HOME

MODULE_HOME = os.path.join(MAIN_HOME, 'btbu')
UNRAR_PATH = os.path.join(MAIN_HOME, 'bin', 'unrar.linux')
if platform.system().lower() == 'windows':
    UNRAR_PATH = os.path.join(MAIN_HOME, 'bin', 'unrar.win.exe')

