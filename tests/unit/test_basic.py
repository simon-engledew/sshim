import unittest, time, os

import sshim, paramiko
from time import sleep

class TestBasic(unittest.TestCase):
    def test_echo(self):
        def echo(script):
            groups = script.expect('(?P<value>.*)').groupdict()
            assert groups['value'] == 'test_echo'
            script.writeline('%(value)s' % groups)

        with sshim.Server(echo, port=3000) as server:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('127.0.0.1', port=3000)
            channel = ssh.invoke_shell()
            fileobj = channel.makefile('rw')
            fileobj.write('test_echo\n')
            response = fileobj.readline()
            assert response == 'test_echo\r\n'
