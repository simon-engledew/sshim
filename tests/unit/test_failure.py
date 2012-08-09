import unittest
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

    def test_eof(self):
        def echo(script):
            script.expect('goose')

        with sshim.Server(echo, port=3000):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('127.0.0.1', port=3000)
            channel = ssh.invoke_shell()
            fileobj = channel.makefile('rw')
            fileobj.write('goose\n')
            fileobj.flush()
            fileobj.close()

            ssh.close()

    def test_remainder(self):
        def echo(script):
            script.expect('moose')
            self.assertRaises(AssertionError, script.expect, '')

        with sshim.Server(echo, port=3000):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('127.0.0.1', port=3000)
            channel = ssh.invoke_shell()
            fileobj = channel.makefile('rw')
            fileobj.write('moose\n')
            fileobj.write('goose\n')
            fileobj.flush()
            fileobj.close()

            ssh.close()
