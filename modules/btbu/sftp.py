#!/usr/bin/env python
# -*- coding:utf-8 -*-
import paramiko
import socket
import os
from stat import S_ISDIR

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

    def __init__(self, hostname, username='root', password=None, port=22, timeout=5):
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
        self.bloom = dict()

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

    def remotepath_join(self, *args):
        #  Bug fix for Windows clients, we always use / for remote paths
        return '/'.join(args)

    def put_all(self, localpath, remotepath):
        #  recursively upload a full directory
        os.chdir(os.path.split(localpath)[0])
        parent = os.path.split(localpath)[1]
        for path, _, files in os.walk(parent):
            try:
                self.sftp.mkdir(self.remotepath_join(remotepath, path))
            except:
                pass
            for filename in files:
                self.put(os.path.join(path, filename), self.remotepath_join(remotepath, path, filename))

    def get(self, remotefile, localfile):
        #  Copy remotefile to localfile, overwriting or creating as needed.
        self.sftp.get(remotefile, localfile)

    def downloaded(self, remote_filepath):
        md5 = self.command('md5sum ' + remote_filepath)[:32]
        if md5 not in self.bloom:
            self.bloom[md5] = remote_filepath
            return False
        return True

    def sftp_walk(self, remotepath):
        # Kindof a stripped down  version of os.walk, implemented for
        # sftp.  Tried running it flat without the yields, but it really
        # chokes on big directories.
        path = remotepath
        files = []
        folders = []
        for f in self.sftp.listdir_attr(remotepath):
            if S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        yield path, folders, files
        for folder in folders:
            new_path = self.remotepath_join(remotepath, folder)
            for x in self.sftp_walk(new_path):
                yield x

    def get_all(self, remotepath, localpath):
        #  recursively download a full directory
        #  Harder than it sounded at first, since paramiko won't walk
        #
        # For the record, something like this would gennerally be faster:
        # ssh user@host 'tar -cz /source/folder' | tar -xz

        self.sftp.chdir(os.path.split(remotepath)[0])
        parent = os.path.split(remotepath)[1]
        try:
            os.mkdir(localpath)
        except FileExistsError:
            pass
        for path, _, files in self.sftp_walk(parent):
            try:
                os.mkdir(self.remotepath_join(localpath, path))
            except FileExistsError:
                pass
            for filename in files:
                remote_filepath = self.remotepath_join(path, filename)
                if self.downloaded(remote_filepath):
                    print('>> downloaded:', remote_filepath)
                    continue
                print(remote_filepath, '\t', os.path.join(localpath, path, filename))
                self.get(remote_filepath, os.path.join(localpath, path, filename))

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
    s.get_all('/root/xdocker', r'D:\PycharmProjects\secrawler\zdump')
    # print(s.command('md5sum /root/xdocker/maltrace.zip'))
    # print(s.command('ls -lh /etc/nginx/'))
    s.close()

