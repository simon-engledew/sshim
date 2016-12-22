import paramiko
import unittest
import sshim
from . import connect

def success(script):
    script.writeline('success')

class TestMultipleServers(unittest.TestCase):
    def assert_success(self, server):
        with connect(server) as fileobj:
            self.assertEqual(fileobj.readline(), 'success\r\n')

    def test_one_after_another_reuse(self):
        with sshim.Server(success, address='127.0.0.1', port=3000) as server:
            self.assert_success(server)

        with sshim.Server(success, address='127.0.0.1', port=3000) as server:
            self.assert_success(server)

    def test_another_server_reuse(self):
        with sshim.Server(success, address='127.0.0.1', port=3000) as server:
            self.assert_success(server)

    def test_one_after_another_different(self):
        with sshim.Server(success, address='127.0.0.1', port=0) as server:
            self.assert_success(server)

        with sshim.Server(success, address='127.0.0.1', port=0) as server:
            self.assert_success(server)

    def test_another_server_different(self):
        with sshim.Server(success, address='127.0.0.1', port=0) as server:
            self.assert_success(server)
