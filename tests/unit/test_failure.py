import unittest
import sshim
import paramiko
from . import connect

class TestFailure(unittest.TestCase):
    def test_unexpected(self):
        def echo(script):
            script.expect('moose')
            script.writeline('return')

        with sshim.Server(echo, address='127.0.0.1', port=0) as server:
            with connect(server) as fileobj:
                fileobj.write('goose\n')
                fileobj.flush()
                server.exceptions.get()

    def test_eof(self):
        def echo(script):
            script.expect('goose')
            self.assertRaises(EOFError, script.expect, '')

        with sshim.Server(echo, address='127.0.0.1', port=0) as server:
            with connect(server) as fileobj:
                fileobj.write('goose\n')
                fileobj.flush()
                fileobj.close()

    def test_remainder(self):
        def echo(script):
            script.expect('moose')
            self.assertRaises(AssertionError, script.expect, '')

        with sshim.Server(echo, address='127.0.0.1', port=0) as server:
            with connect(server) as fileobj:
                fileobj.write('moose\n')
                fileobj.write('goose\n')
                fileobj.flush()
                fileobj.close()
