import unittest
import re
import sshim
import paramiko

class TestBasic(unittest.TestCase):
    def test_echo(self):
        def echo(script):
            groups = script.expect(re.compile('(?P<value>.*)')).groupdict()
            assert groups['value'] == 'test_echo'
            script.writeline('return %(value)s' % groups)

        with sshim.Server(echo, port=3000):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect('127.0.0.1', port=3000)
            channel = ssh.invoke_shell()
            fileobj = channel.makefile('rw')
            fileobj.write('test_echo\n')
            fileobj.flush()
            assert fileobj.readline() == 'test_echo\r\n'
            assert fileobj.readline() == 'return test_echo\r\n'
            ssh.close()
