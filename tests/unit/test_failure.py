import unittest
import re
import sshim
import paramiko

class TestFailure(unittest.TestCase):
    def test_unexpected(self):
        def echo(script):
            script.expect('moose')
            script.writeline('return')

        with sshim.Server(echo, port=3000) as server:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('127.0.0.1', port=3000)
            channel = ssh.invoke_shell()
            fileobj = channel.makefile('rw')
            fileobj.write('goose\n')
            fileobj.flush()
            server.exceptions.get()
            ssh.close()

    def test_remainder(self):
        def echo(script):
            pass

        with sshim.Server(echo, port=3000) as server:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('127.0.0.1', port=3000)
            channel = ssh.invoke_shell()
            fileobj = channel.makefile('rw')
            fileobj.write('goose\n')
            fileobj.flush()
            ssh.close()

        # self.assertFalse(server.exceptions.empty())

            # self.assertFalse(not server.exceptions.empty())
            # server.exceptions.get()

            # ssh.close()
