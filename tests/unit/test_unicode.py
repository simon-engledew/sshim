# -*- coding: utf8 -*-

import unittest
import sshim
import paramiko
import re
import codecs
import six

from . import connect

class TestUnicode(unittest.TestCase):
    def test_unicode_echo(self):
        def decode(value):
          if isinstance(value, six.text_type):
            return value
          return codecs.decode(value, 'utf8')

        def echo(script):
            groups = script.expect(re.compile(six.u('(?P<value>.*)'))).groupdict()
            value = groups['value']
            assert value == six.u('£test')
            script.writeline(six.u('return {0}').format(value))

        with sshim.Server(echo, address='127.0.0.1', port=0, encoding='utf8') as server:
            with connect(server) as fileobj:
                fileobj.write(six.u('£test\n').encode('utf8'))
                fileobj.flush()
                assert decode(fileobj.readline()) == six.u('£test\r\n')
                assert decode(fileobj.readline()) == six.u('return £test\r\n')
