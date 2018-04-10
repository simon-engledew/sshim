import unittest
import re
import sshim
from . import connect

class TestBasic(unittest.TestCase):
    def test_wildcard_host(self):
        def echo(script):
            groups = script.expect(re.compile('(?P<value>.*)')).groupdict()
            assert groups['value'] == 'test_echo'
            script.writeline('return %(value)s' % groups)

        with sshim.Server(echo, port=0) as server:
            with connect(server) as fileobj:
                fileobj.write('test_echo\n')
                fileobj.flush()
                assert fileobj.readline() == 'test_echo\r\n'
                assert fileobj.readline() == 'return test_echo\r\n'

    def test_echo_ipv4(self):
        def echo(script):
            groups = script.expect(re.compile('(?P<value>.*)')).groupdict()
            assert groups['value'] == 'test_echo'
            script.writeline('return %(value)s' % groups)

        with sshim.Server(echo, address='127.0.0.1', port=0) as server:
            with connect(server) as fileobj:
                fileobj.write('test_echo\n')
                fileobj.flush()
                assert fileobj.readline() == 'test_echo\r\n'
                assert fileobj.readline() == 'return test_echo\r\n'

    def test_echo_ipv6(self):
        def echo(script):
            groups = script.expect(re.compile('(?P<value>.*)')).groupdict()
            assert groups['value'] == 'test_echo'
            script.writeline('return %(value)s' % groups)

        with sshim.Server(echo, address='::1', port=0) as server:
            with connect(server) as fileobj:
                fileobj.write('test_echo\n')
                fileobj.flush()
                assert fileobj.readline() == 'test_echo\r\n'
                assert fileobj.readline() == 'return test_echo\r\n'
