# -*- coding: utf8 -*-

import unittest
import sshim
import paramiko
import re

from . import connect

class TestUnicode(unittest.TestCase):
    def test_unicode_echo(self):
        def decode(value):
            if hasattr(value, 'decode'):
                return value.decode('utf8')
            return value

        def echo(script):
            groups = script.expect(re.compile(u'(?P<value>.*)')).groupdict()
            value = groups['value']
            assert value == u'£test'
            script.writeline(u'return {0}'.format(value))

        with sshim.Server(echo, port=3000, encoding='utf8') as server:
            with connect(server) as fileobj:
                fileobj.write(u'£test\n'.encode('utf8'))
                fileobj.flush()
                assert decode(fileobj.readline()) == u'£test\r\n'
                assert decode(fileobj.readline()) == u'return £test\r\n'
