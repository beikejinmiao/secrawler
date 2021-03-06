#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tika
from tika import parser
import json
import time
import re
import shutil
import rarfile
import traceback
from multiprocessing import Queue, Process
from py7zr import pack_7zarchive, unpack_7zarchive
import pandas as pd
from id_validator import validator
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))
from utils import tree2list
from libs.timer import timer
from libs.regex import img, video, executable, archive, doc, plain_text, html, js_css
from utils import traverse
from modules.btbu.util import find_idcard
from modules.btbu.config import UNRAR_PATH
from modules.btbu.config import SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD
from modules.btbu.sftp.client import SSHSession
from paths import DUMP_HOME, DOWNLOADS
from libs.logger import logger


shutil.register_archive_format('7zip',
                               pack_7zarchive,
                               description='7zip archive')
shutil.register_unpack_format('7zip',
                              ['.7z'],
                              unpack_7zarchive,
                              description='7zip archive')


def unpack(root, dstdir=''):
    files = traverse(root)
    failed_count = 0
    for filepath in files:
        if not archive.match(filepath):
            continue
        try:
            if re.match(r'.*\.rar$', filepath, re.I):
                rarfile.UNRAR_TOOL = UNRAR_PATH
                rar = rarfile.RarFile(filepath)
                with rar as rf:
                    rf.extractall(dstdir)
            else:
                # shutil.ReadError: xxx.zip is not a zip file
                shutil.unpack_archive(filepath, dstdir)
        except:
            logger.error('unpack error: %s' % filepath)
            logger.error(traceback.format_exc())
            failed_count += 1
        unpack(dstdir)  # 最多支持两层压缩

    return failed_count


class Manager(object):
    def __init__(self):
        self.queue = Queue(100000)
        #
        self.counter = {
            'que_get': 0,
            'archive': 0,
            'doc': 0,
            'others': 0,
        }

    def sftp(self, remote_dir):
        ssh = SSHSession(hostname=SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, queue=self.queue)
        ssh.run(remote_dir)

    def _extract(self, root):
        results = dict()
        files = traverse(root)
        for filepath in files:
            candidates = list()
            try:
                # 过滤图片、音视频、可执行程序
                if img.match(filepath) or video.match(filepath) or \
                        archive.match(filepath) or executable.match(filepath):
                    continue
                #
                if doc.match(filepath):
                    self.counter['doc'] += 1
                else:
                    self.counter['others'] += 1
                logger.info("Load: '%s'" % filepath)
                # 普通文本文件、HTML、JS、CSS文件直接读取解析
                if plain_text.match(filepath) or html.match(filepath) or js_css.match(filepath):
                    try:
                        with open(filepath, encoding='gbk') as fopen:
                            candidates.extend(find_idcard(fopen.read()))
                    except UnicodeDecodeError:
                        with open(filepath, encoding='utf-8') as fopen:
                            candidates.extend(find_idcard(fopen.read()))
                    # gbk/utf-8均解码错误，使用tika解析
                    except:
                        parsed = parser.from_file(filepath)
                        candidates.extend(find_idcard(parsed["content"]))
                else:
                    parsed = parser.from_file(filepath)
                    candidates.extend(find_idcard(parsed["content"]))
            except:
                logger.error(traceback.format_exc())
            if len(candidates) > 0:
                results[filepath] = list(candidates)
        return results

    def extract(self):
        infos = dict()

        # 每2分钟保存一次现有结果
        @timer(120, 120)
        def dump2csv():
            df = pd.DataFrame(tree2list(infos), columns=['filepath', 'idcard'])
            df = df.assign(idcard=df["idcard"]).explode("idcard").reset_index(drop=True)
            df['is_valid'] = df['idcard'].map(lambda x: 1 if validator.is_valid(x) else 0)
            # 移除本地路径
            df['filepath'] = df['filepath'].map(lambda x: x[len(DOWNLOADS):].replace('.unpack', ''))
            # excel/wps无法处理15位以上的数字,所以需添加引号修改单元格格式位文本后移除引号
            df['idcard'] = df['idcard'].map(lambda x: "'%s'" % x)
            df.to_csv(os.path.join(DUMP_HOME, 'results.csv'))
            logger.info('Extractor count stats: %s' % json.dumps(self.counter))

        dump2csv()
        # 无法根据queue是否empty自动退出(如果处理快于下载导致queue多数时间为空)
        while True:
            filepath = self.queue.get(block=True)     # 阻塞至项目可得到
            self.counter['que_get'] += 1
            results = None
            if img.match(filepath) or video.match(filepath) or executable.match(filepath):
                continue
            if archive.match(filepath):
                self.counter['archive'] += 1
                logger.info("Unpack: '%s'" % filepath)
                dstdir = filepath + '.unpack'
                unpack(filepath, dstdir=dstdir)
                results = self._extract(dstdir)
                shutil.rmtree(dstdir, ignore_errors=True)
            else:
                results = self._extract(filepath)
            if results:
                infos.update(results)
            os.remove(filepath)

    def run(self):
        ps_sftp = Process(target=self.sftp, name='sftp', args=('/data/publish',))
        ps_ext = Process(target=self.extract, name='extract')
        ps_sftp.start()
        ps_ext.start()
        while True:
            time.sleep(60)
        # TODO: sftp进程结束后会导致extract进行同时结束
        # ps_sftp.join()  # 等待下载结束
        # logger.info('Download Completed.')
        # while True:
        #     time.sleep(60)
        #     # 等待处理结束
        #     if not self.queue.empty():
        #         time.sleep(60)
        #         continue
        #     # 等待最后一个文件被处理完毕
        #     if self.queue.empty():
        #         logger.info('Extract Completed.')
        #         time.sleep(60)
        #     sys.exit(0)


if __name__ == '__main__':
    manager = Manager()
    try:
        manager.run()
    except KeyboardInterrupt:
        logger.info('Extractor count stats: %s' % json.dumps(manager.counter))

