import paramiko
import unittest
import sshim
import re

def success(script):
    script.writeline('success')

class TestMultipleServers(unittest.TestCase):
    def assert_success(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('127.0.0.1', port=3000)
        channel = ssh.invoke_shell()
        fileobj = channel.makefile('rw')
        self.assertEqual(fileobj.readline(), 'success\r\n')
        ssh.close()

    def test_one_after_another(self):
        with sshim.Server(success, port=3000) as server:
            self.assert_success()

        with sshim.Server(success, port=3000) as server:
            self.assert_success()

    def test_another_server(self):
        with sshim.Server(success, port=3000) as server:
            self.assert_success()