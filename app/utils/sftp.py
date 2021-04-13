# -*- coding: utf8 -*-
__author__ = 'YNYANG'
__time__ = '2019/5/7'

import paramiko


class SFTP(object):
    def __init__(self, ip, password, port=22, user='root'):
        self.ssh = None
        self.sftp = None
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password

    def ssh_open(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.ip, self.port, self.user, self.password)

    def sftp_open(self):
        self.ssh_open()
        self.sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
        self.sftp = self.ssh.open_sftp()

    def sftp_put(self, local_file, remote_file):
        self.sftp.put(local_file, remote_file)

    def sftp_get(self, remote_file, local_file):
        self.sftp.get(remote_file, local_file)

    def ssh_execute(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout.read()

    def close(self):
        self.ssh.close()
