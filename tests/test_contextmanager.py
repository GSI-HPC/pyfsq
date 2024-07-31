"""Suite for testing FSQ contextmanager functionality."""

import os
import random
import unittest
from fsq.contextmanager import Connect, Open
from fsq.struct import FsqStorageDest, FsqProtocolState
from fsq.misc import generate_random_str

class TestFsqContextManager(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestFsqContextManager, self).__init__(*args, **kwargs)

    def test_connect(self):
        with Connect('polaris', 'polaris', '127.0.0.1', 7625) as fsq:
            self.assertGreater(fsq.sock.fileno(), -1)
            self.assertEqual(fsq.fsq_packet.state, FsqProtocolState.FSQ_CONNECT)
        self.assertEqual(fsq.sock.fileno(), -1)
        self.assertEqual(fsq.fsq_packet.state, FsqProtocolState.FSQ_DISCONNECT)

    def test_open_write(self):
        with Connect('polaris', 'polaris', 'localhost', 7625) as fsq:
            for _ in range(15):
                with Open(fsq, '/lustre', '/lustre/ctxmgr/' + generate_random_str(32),
                          'some description', FsqStorageDest.FSQ_STORAGE_LOCAL):
                    for _ in range(5):
                        size = random.randint(1, 0xFFFF)
                        buffer = os.urandom(size)
                        fsq.write(buffer, size)
                        self.assertEqual(fsq.fsq_packet.state,
                                         FsqProtocolState.FSQ_DATA)
                self.assertEqual(fsq.fsq_packet.state, FsqProtocolState.FSQ_CLOSE)
        self.assertEqual(fsq.sock.fileno(), -1)
        self.assertEqual(fsq.fsq_packet.state, FsqProtocolState.FSQ_DISCONNECT)

if __name__ == '__main__':
    unittest.main()
