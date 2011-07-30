import unittest, time, os

import sshim

class TestExec(unittest.TestCase):
    def test_listen(self):
        with sshim.SSHServer(3000) as server:
            #assert os.system('ssh 127.0.0.1 -p 3000 "echo hello"') == 0
            pass
