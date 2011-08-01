import unittest, time, os

import sshim, paramiko
from time import sleep

class TestExec(unittest.TestCase):
    def test_echo(self):
        def echo(script):
            script << '(?P<value>.*)'
            assert script.values.get('value') == 'test_echo'
            script >> '%(value)s'
        
        with sshim.SSHim(echo, port=3000) as server:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('127.0.0.1', port=3000)
            channel = ssh.invoke_shell()
            fileobj = channel.makefile('rw')
            fileobj.write('test_echo\n')
            assert fileobj.readline() == 'test_echo\r\n'
