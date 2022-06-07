#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import paramiko
import socket
import traceback
from stat import S_ISDIR
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))
from paths import DOWNLOADS
from libs.logger import logger


class SSHSession(object):
    def __init__(self, hostname, username='root', password=None, port=22, timeout=5):
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
        self.files = []
        self.fopen = open('/tmp/sftp_files.txt', 'w')
        self.counter = {
            'sftp_find': 0,
            'img_video_exe': 0,
        }

    @staticmethod
    def _path_join(*args):
        #  Bug fix for Windows clients, we always use / for remote paths
        return '/'.join(args)

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

    def get_all(self, remote_dir, local_dir):
        home = os.path.split(remote_dir)[0]
        self.sftp.chdir(home)
        parent = os.path.split(remote_dir)[1]
        try:
            os.mkdir(local_dir)
        except FileExistsError:
            pass
        try:
            for path, _, files in self.sftp_walk(parent):
                try:
                    os.mkdir(self._path_join(local_dir, path))
                except FileExistsError:
                    pass
                for filename in files:
                    self.counter['sftp_find'] += 1
                    if self.counter['sftp_find'] % 2000 == 0:
                        logger.info('count: %s' % self.counter['sftp_find'])
                        self.fopen.flush()
                    remote_filepath = self._path_join(home, path, filename)
                    self.files.append(remote_filepath)
                    self.fopen.write(remote_filepath + '\n')
        except:
            logger.error('sftp get all error: %s' % remote_dir)
            logger.info(traceback.format_exc())
        logger.info('Total file count: %s' % self.counter['sftp_find'])
        self.fopen.close()


if __name__ == '__main__':
    s = SSHSession(hostname='10.0.33.50', port=22, username='grxxjc', password='gRxXjc)%3!')
    try:
        s.get_all('/data/publish', DOWNLOADS)
    except KeyboardInterrupt:
        if not s.fopen.closed:
            s.fopen.close()
