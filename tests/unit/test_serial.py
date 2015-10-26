import paramiko
import unittest
import sshim

def success(script):
    script.writeline('success')

class TestMultipleServers(unittest.TestCase):
    def assert_success(self, port):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('0.0.0.0', port=port)
        channel = ssh.invoke_shell()
        fileobj = channel.makefile('rw')
        self.assertEqual(fileobj.readline(), 'success\r\n')
        ssh.close()

    def test_one_after_another(self):
        port = 0

        with sshim.Server(success, port=0) as server:
            port = server.port
            self.assert_success(port)

        with sshim.Server(success, port=port):
            self.assert_success(port)

    def test_another_server(self):
        with sshim.Server(success, port=0) as server:
            self.assert_success(server.port)