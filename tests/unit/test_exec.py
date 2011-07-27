import unittest, time, os

import sshim

class TestExec(unittest.TestCase):
    def test_listen(self):
        host = sshim.Host(3000)
        host.start()
        print 'start'
        
        assert os.system('ssh 127.0.0.1 -p 3000 "echo hello"') == 0
        
        host.stop()
        print 'stop'
