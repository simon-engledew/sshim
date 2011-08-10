import unittest, time, os

import sshim, paramiko
from time import sleep

class TestBasic(unittest.TestCase):
    def test_echo(self):
        def echo(script):
            script.expect('(?P<value>.*)')
            assert script['value'] == 'test_echo'
            script.writeline('%(value)s')

        with sshim.Server(echo, port=3000) as server:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('127.0.0.1', port=3000)
            channel = ssh.invoke_shell()
            fileobj = channel.makefile('rw')
            fileobj.write('test_echo\n')
            assert fileobj.readline() == 'test_echo\r\n'
