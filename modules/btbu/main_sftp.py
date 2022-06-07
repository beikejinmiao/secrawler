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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
from utils import tree2list
from libs.timer import timer, processed
from libs.regex import img, video, executable, archive, doc
from utils import reader, traverse
from modules.btbu.util import find_idcard
from modules.btbu.config import UNRAR_PATH
from modules.btbu.sftp import SSHSession, SSH_HOST, SSH_PORT, SSH_USER, SSH_PASSWORD
from paths import DOWNLOADS, DUMP_HOME
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

    # @processed(start=True)
    def download(self, remote):
        ssh = SSHSession(hostname=SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD, queue=self.queue)
        ssh.get_all(remote, DOWNLOADS)

    def _extract(self, root):
        results = dict()
        files = traverse(root)
        for filepath in files:
            candidates = list()
            try:
                if img.match(filepath) or video.match(filepath) or archive.match(filepath) or executable.match(
                        filepath):
                    continue
                logger.info("Load: '%s'" % filepath)
                if doc.match(filepath):
                    self.counter['doc'] += 1
                else:
                    self.counter['others'] += 1
                parsed = parser.from_file(filepath)
                candidates.extend(find_idcard(parsed["content"]))
            except:
                logger.error(traceback.format_exc())
            if len(candidates) > 0:
                results[filepath] = list(candidates)
        return results

    # @processed(start=True)
    def extract(self):
        infos = dict()

        # 每2分钟保存一次现有结果
        @timer(120, 120)
        def dump2csv():
            df = pd.DataFrame(tree2list(infos), columns=['filepath', 'idcard'])
            df = df.assign(idcard=df["idcard"]).explode("idcard").reset_index(drop=True)
            df['is_valid'] = df['idcard'].map(lambda x: 1 if validator.is_valid(x) else 0)
            df.to_csv(os.path.join(DUMP_HOME, 'results.csv'))
            logger.info('Extractor count stats: %s' % json.dumps(self.counter))

        dump2csv()
        # 无法根据queue是否empty自动退出(如果处理快于下载导致queue多数时间为空)
        while True:
            filepath = self.queue.get(block=True)     # 阻塞至项目可得到
            self.counter['que_get'] += 1
            logger.debug('Get: %s' % filepath)
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
        ps_down = Process(target=self.download, name='download', args=('/data/publish',))
        ps_ext = Process(target=self.extract, name='extract')
        ps_down.start()
        ps_ext.start()
        ps_down.join()  # 等待下载结束
        logger.info('Download Completed.')
        while True:
            # 等待处理结束
            if not self.queue.empty():
                time.sleep(60)
                continue
            # 等待最后一个文件被处理完毕
            if self.queue.empty():
                logger.info('Extract Completed.')
                time.sleep(60)
            sys.exit(0)


if __name__ == '__main__':
    manager = Manager()
    try:
        manager.run()
    except KeyboardInterrupt:
        logger.info('Extractor count stats: %s' % json.dumps(manager.counter))


