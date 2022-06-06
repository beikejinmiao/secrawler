#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import paramiko
import socket
import os
import json
import traceback
from stat import S_ISDIR
from queue import Full
from libs.timer import timer
from libs.regex import img, video, executable
from modules.btbu.util import downloaded_md5
from libs.logger import logger

"""
https://gist.github.com/johnfink8/2190472
"""

SSH_HOST = '10.0.33.50'
SSH_PORT = 22
SSH_USER = 'grxxjc'
SSH_PASSWORD = 'gRxXjc)%3!'


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
        #
        #  Accepts a file-like object (anything with a readlines() function)
        #  in either dss_key or rsa_key with a private key.  Since I don't
        #  ever intend to leave a server open to a password auth.
        #
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
        # self.bloom = BloomFilter(max_elements=1000000, error_rate=0.001)
        self.bloom = downloaded_md5()
        self.queue = queue
        #
        self.counter = {
            'sftp_find': 0,
            'download': 0,
            'que_put': 0,
            'img_video_exe': 0,
        }
        self._log_stats()

    @timer(120, 120)
    def _log_stats(self):
        logger.info('Downloader count stats: %s' % json.dumps(self.counter))

    def command(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd, get_pty=True)
        out = stdout.read()
        # 执行状态,0表示成功，1表示失败
        if stdout.channel.recv_exit_status() != 0:
            return None
        return str(out, encoding='utf-8')

    def put(self, localfile, remotefile):
        #  Copy localfile to remotefile, overwriting or creating as needed.
        self.sftp.put(localfile, remotefile)

    @staticmethod
    def _path_join(*args):
        #  Bug fix for Windows clients, we always use / for remote paths
        return '/'.join(args)

    def put_all(self, localpath, remotepath):
        #  recursively upload a full directory
        os.chdir(os.path.split(localpath)[0])
        parent = os.path.split(localpath)[1]
        for path, _, files in os.walk(parent):
            try:
                self.sftp.mkdir(self._path_join(remotepath, path))
            except:
                pass
            for filename in files:
                self.put(os.path.join(path, filename), self._path_join(remotepath, path, filename))

    def get(self, remotefile, localfile):
        #  Copy remotefile to localfile, overwriting or creating as needed.
        try:
            self.sftp.get(remotefile, localfile)
            self.counter['download'] += 1
        except:
            logger.error(traceback)
            logger.error('sftp get error:%s - %s' % (remotefile, localfile))

    def is_downloaded(self, remote_filepath):
        try:
            # TypeError: 'NoneType' object is not subscriptable
            md5 = self.command('md5sum ' + remote_filepath)[:32]
            if md5 in self.bloom:
                return True
            self.bloom[md5] = remote_filepath
        except:
            logger.error('check downloaded error: %s' % remote_filepath)
            logger.error(traceback.format_exc())
        return False

    def sftp_walk(self, remotepath):
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
            for x in self.sftp_walk(new_path):
                yield x

    def _put_to_queue(self, filepath):
        if self.queue is None:
            return
        # 当queue长度大于100时等待消费端处理,避免堆积过多导致占用过多磁盘空间
        while self.queue.qsize() > 100:
            logger.debug('Queue size greater than 100, sleep 10s.')
            time.sleep(10)
        self.queue.put(filepath, block=True)        # 阻塞至有空闲槽可用
        self.counter['que_put'] += 1
        logger.debug('Put: %s' % filepath)
        # while True:
        #     try:
        #         self.queue.put(filepath)
        #     except Full:
        #         time.sleep(5)
        #         continue
        #     except:
        #         logger.error(traceback.format_exc())
        #     break

    def get_all(self, remote_dir, local_dir):
        #  recursively download a full directory
        #  Harder than it sounded at first, since paramiko won't walk
        #
        # For the record, something like this would gennerally be faster:
        # ssh user@host 'tar -cz /source/folder' | tar -xz
        home = os.path.split(remote_dir)[0]
        self.sftp.chdir(home)
        parent = os.path.split(remote_dir)[1]
        try:
            os.mkdir(local_dir)
        except FileExistsError:
            pass
        for path, _, files in self.sftp_walk(parent):
            try:
                os.mkdir(self._path_join(local_dir, path))
            except FileExistsError:
                pass
            for filename in files:
                self.counter['sftp_find'] += 1
                remote_filepath = self._path_join(home, path, filename)
                if img.match(filename) or video.match(filename) or executable.match(filename):
                    self.counter['img_video_exe'] += 1
                    logger.debug('Ignore: %s' % remote_filepath)
                    continue
                if self.is_downloaded(remote_filepath):
                    logger.info('Downloaded: %s' % remote_filepath)
                    continue
                local_filepath = os.path.join(local_dir, path, filename)
                logger.info('Download: %s\t%s' % (remote_filepath, local_filepath))
                self.get(remote_filepath, local_filepath)
                self._put_to_queue(local_filepath)

    def write_command(self, text, remotefile):
        #  Writes text to remotefile, and makes remotefile executable.
        #  This is perhaps a bit niche, but I was thinking I needed it.
        #  For the record, I was incorrect.
        self.sftp.open(remotefile, 'w').write(text)
        self.sftp.chmod(remotefile, 755)

    def close(self):
        self.t.close()
        self.ssh.close()


if __name__ == '__main__':
    s = SSHSession(hostname='106.13.202.41', port=61001, password='')
    s.get_all('/root/xdocker', r'D:\PycharmProjects\secrawler\zdump\downloads')
    # print(s.command('md5sum /root/xdocker/maltrace.zip'))
    # print(s.command('ls -lh /etc/nginx/'))
    s.close()

