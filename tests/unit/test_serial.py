import unittest
import sshim
import re

def echo(script):
    groups = script.expect(re.compile('(?P<value>.*)')).groupdict()
    script.writeline('%(value)s' % groups)

class TestMultipleServers(unittest.TestCase):
    def test_one_after_another(self):
        with sshim.Server(echo, port=3000) as server:
            self.assertTrue(server)

        with sshim.Server(echo, port=3000) as server:
            self.assertTrue(server)

    def test_another_server(self):
        with sshim.Server(echo, port=3000) as server:
            self.assertTrue(server)