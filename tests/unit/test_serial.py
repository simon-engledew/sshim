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
            fileobj.close()

    def test_one_after_another(self):
        with sshim.Server(success, port=3000) as server:
            self.assert_success(server)

        with sshim.Server(success, port=3000) as server:
            self.assert_success(server)

    def test_another_server(self):
        with sshim.Server(success, port=3000) as server:
            self.assert_success(server)