#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import paramiko
import socket
import os
import json
import traceback
from stat import S_ISDIR
from paths import DUMP_HOME, DOWNLOADS
from libs.timer import timer
from libs.regex import img, video, executable
from libs.logger import logger


"""
https://gist.github.com/johnfink8/2190472
"""


class SSHSession(object):
    # Usage:
    # Detects DSA or RSA from key_file, either as a string filename or a
    # file object.  Password auth is possible, but I will judge you for
    # using it. So:
    # ssh=SSHSession('targetserver.com','root',key_file=open('mykey.pem','r'))
    # ssh=SSHSession('targetserver.com','root',key_file='/home/me/mykey.pem')
    # ssh=SSHSession('targetserver.com','root','mypassword')
    # ssh.put('filename','/remote/file/destination/path')
    # ssh.put_all('/path/to/local/source/dir','/path/to/remote/destination')
    # ssh.get_all('/path/to/remote/source/dir','/path/to/local/destination')
    # ssh.command('echo "Command to execute"')

    def __init__(self, hostname, username='root', password=None, port=22, timeout=5, queue=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((hostname, port))
        self.t = paramiko.Transport(self.sock)
        self.t.banner_timeout = timeout
        self.t.start_client()
        if password is not None:
            self.t.auth_password(username, password, fallback=False)
        else:
            raise Exception('Must supply either key_file or password')
        self.sftp = paramiko.SFTPClient.from_transport(self.t)

        # Create object of SSHClient and connecting to SSH
        self.ssh = paramiko.SSHClient()
        # Adding new host key to the local
        # HostKeys object(in case of missing)
        # AutoAddPolicy for missing host key to be set before connection setup.
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(hostname, port=port, username=username, password=password, timeout=timeout)
        #
        self.queue = queue
        self.files = []
        self.fopen = open(os.path.join(DUMP_HOME, 'filepath.txt'), 'w')
        #
        self.counter = {
            'sftp_find': 0,
            'download': 0,
            'que_put': 0,
            'img_video_exe': 0,
        }

    @timer(120, 120)
    def _log_stats(self):
        logger.info('Downloader count stats: %s' % json.dumps(self.counter))

    @staticmethod
    def _path_join(*args):
        #  Bug fix for Windows clients, we always use / for remote paths
        return '/'.join(args)

    def _sftp_walk(self, remotepath):
        # Kindof a stripped down  version of os.walk, implemented for
        # sftp.  Tried running it flat without the yields, but it really
        # chokes on big directories.
        path = remotepath
        files = []
        folders = []
        try:
            # UnicodeDecodeError
            for f in self.sftp.listdir_attr(remotepath):
                if S_ISDIR(f.st_mode):
                    folders.append(f.filename)
                else:
                    files.append(f.filename)
        except:
            logger.error('sftp walk error: %s' % remotepath)
            logger.error(traceback.format_exc())

        yield path, folders, files

        for folder in folders:
            new_path = self._path_join(remotepath, folder)
            for x in self._sftp_walk(new_path):
                yield x

    def traverse(self, remote_dir):
        home = os.path.split(remote_dir)[0]
        self.sftp.chdir(home)
        parent = os.path.split(remote_dir)[1]
        try:
            for path, _, files in self._sftp_walk(parent):
                for filename in files:
                    self.counter['sftp_find'] += 1
                    if self.counter['sftp_find'] % 2000 == 0:
                        logger.info('count: %s' % self.counter['sftp_find'])
                        self.fopen.flush()
                    remote_filepath = self._path_join(home, path, filename)
                    self.fopen.write(remote_filepath + '\n')
                    # 过滤图片、音视频、可执行程序
                    if img.match(remote_filepath) or video.match(remote_filepath) or executable.match(remote_filepath):
                        self.counter['img_video_exe'] += 1
                        logger.debug('Ignore: %s' % remote_filepath)
                        continue
                    self.files.append(remote_filepath)
        except:
            logger.error('sftp traverse error: %s' % remote_dir)
            logger.info(traceback.format_exc())
        logger.info('Traverse done.\nTotal file count: %s. Valid file count: %s' %
                    (self.counter['sftp_find'], len(self.files)))
        self.fopen.close()

    def download(self):
        for remote_filepath in self.files:
            # 创建本地目录
            local_filepath = os.path.join(DOWNLOADS, remote_filepath[1:])   # 两个绝对路径join之后是最后一个绝对路径
            local_dir = os.path.dirname(local_filepath)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
            # 下载
            try:
                self.sftp.get(remote_filepath, local_filepath)
                self.counter['download'] += 1
                logger.info('Download: %s' % remote_filepath)
            except:
                logger.error(traceback)
                logger.error('Download Error: %s' % remote_filepath)
                continue
            # 将下载文件的本地路径放入队列中
            if self.queue is not None:
                # 当queue长度大于100时等待消费端处理,避免堆积过多导致占用过多磁盘空间
                while self.queue.qsize() > 100:
                    logger.debug('Queue size greater than 100, sleep 10s.')
                    time.sleep(10)
                self.queue.put(local_filepath, block=True)        # 阻塞至有空闲槽可用
                self.counter['que_put'] += 1
        logger.info('Download done.\nDownloader count stats: %s' % json.dumps(self.counter))

    def close(self):
        self.t.close()
        self.ssh.close()
        self.fopen.close()

    def run(self, remote_dir):
        self._log_stats()
        self.traverse(remote_dir)
        self.download()
        self.close()


if __name__ == '__main__':
    s = SSHSession(hostname='106.13.202.41', port=61001, password='')
    s.run('/root/xdocker')
    print(json.dumps(s.counter))
    s.close()
