import os
import unittest

import sshim

def stub_script(script):
    pass

class TestSshimWithoutPrivateKey(unittest.TestCase):
    private_key_path = os.path.join(os.path.dirname(sshim.__file__), 'private.key')
    temp_private_key_path = os.path.join(os.path.dirname(sshim.__file__), 'moved_private.key')

    def setUp(self):
        if os.path.exists(TestSshimWithoutPrivateKey.private_key_path):
            os.rename(TestSshimWithoutPrivateKey.private_key_path, TestSshimWithoutPrivateKey.temp_private_key_path)

    def tearDown(self):
        if os.path.exists(TestSshimWithoutPrivateKey.temp_private_key_path):
            os.rename(TestSshimWithoutPrivateKey.temp_private_key_path, TestSshimWithoutPrivateKey.private_key_path)

    def test_missing_private_key(self):
        self.assertRaises(IOError, sshim.SSHim, stub_script)
