# -*- coding: utf8 -*-

import unittest
import sshim
import ssh
import re

class TestUnicode(unittest.TestCase):
    def test_unicode_echo(self):
        def echo(script):
            groups = script.expect(re.compile(u'(?P<value>.*)')).groupdict()
            value = groups['value'].decode('utf8')
            assert value == u'£test'
            script.writeline(u'return {0}'.format(value).encode('utf8'))

        with sshim.Server(echo, port=0) as server:
            client = ssh.SSHClient()
            client.set_missing_host_key_policy(ssh.AutoAddPolicy())
            client.connect('127.0.0.1', port=server.port)
            shell = client.invoke_shell()
            fileobj = shell.makefile('rw')
            fileobj.write(u'£test\n'.encode('utf8'))
            fileobj.flush()
            assert fileobj.readline().decode('utf8') == u'£test\r\n'
            assert fileobj.readline().decode('utf8') == u'return £test\r\n'
            client.close()
