import sys
sys.path.append('../src')

import unittest
import os
import zlib
import random
import string
import struct
from fsq.api import Api as FsqApi
from fsq.struct import PackUnpackFormat
from fsq.struct import FsqPacket, FsqData, FsqError, FsqInfo, FsqLogin
from fsq.struct import FsqProtocolState, FsqStorageDest
from fsq.struct import PackUnpackFormat, FSQ_PACKET_LENGTH
from fsq.struct import DSM_MAX_NODE_LENGTH, DSM_MAX_VERIFIER_LENGTH
from fsq.struct import DSM_MAX_FSNAME_LENGTH, DSM_MAX_DESCR_LENGTH
from fsq.struct import FSQ_MAX_ERRMSG_LENGTH, HOST_NAME_MAX, PATH_MAX


NUM_REPETITIONS = 1000

def generate_random_ascii(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length)).encode('ascii')

class TestFsqApi(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestFsqApi, self).__init__(*args, **kwargs)
        self.fsqc = FsqApi()

    def test_packet_connect(self):
        for _ in range(0, NUM_REPETITIONS):
            node = generate_random_ascii(DSM_MAX_NODE_LENGTH)
            password = generate_random_ascii(DSM_MAX_VERIFIER_LENGTH)
            hostname = generate_random_ascii(HOST_NAME_MAX)
            port = random.randint(0x1, 0xFFFF)

            self.fsqc.fsq_packet.error = FsqError(rc=random.randint(0x0, 0xFF), strerror=generate_random_ascii(FSQ_MAX_ERRMSG_LENGTH))
            self.fsqc.fsq_packet.state = FsqProtocolState.FSQ_CONNECT
            self.fsqc.fsq_packet.data = FsqLogin(node, password, hostname, port)

            fsq_packet_packed = struct.pack(PackUnpackFormat.CONNECT,
                                            self.fsqc.fsq_packet.ver,
                                            self.fsqc.fsq_packet.error.rc,
                                            self.fsqc.fsq_packet.error.strerror,
                                            self.fsqc.fsq_packet.state,
                                            self.fsqc.fsq_packet.data.node,
                                            self.fsqc.fsq_packet.data.password,
                                            self.fsqc.fsq_packet.data.hostname,
                                            self.fsqc.fsq_packet.data.port)

            self.assertEqual(len(fsq_packet_packed), FSQ_PACKET_LENGTH)
            fsq_packet_unpacked = struct.unpack(PackUnpackFormat.CONNECT, fsq_packet_packed)
            fsq_packet_restored = FsqPacket(ver = fsq_packet_unpacked[0],
                                            error = FsqError(rc = fsq_packet_unpacked[1],
                                                             strerror = fsq_packet_unpacked[2].decode('ascii').strip('\x00').encode('ascii')),
                                            state = fsq_packet_unpacked[3],
                                            data = FsqLogin(fsq_packet_unpacked[4].decode('ascii').strip('\x00').encode('ascii'),
                                                            fsq_packet_unpacked[5].decode('ascii').strip('\x00').encode('ascii'),
                                                            fsq_packet_unpacked[6].decode('ascii').strip('\x00').encode('ascii'),
                                                            fsq_packet_unpacked[7]))

            self.assertEqual(self.fsqc.fsq_packet, fsq_packet_restored)

    def test_packet_open(self):
        for _ in range(0, NUM_REPETITIONS):
            fs = generate_random_ascii(DSM_MAX_FSNAME_LENGTH)
            fpath = generate_random_ascii(PATH_MAX)
            desc = generate_random_ascii(DSM_MAX_DESCR_LENGTH)

            self.fsqc.fsq_packet.error = FsqError(rc=random.randint(0x0, 0xFF), strerror=generate_random_ascii(FSQ_MAX_ERRMSG_LENGTH))
            self.fsqc.fsq_packet.state = FsqProtocolState.FSQ_OPEN
            self.fsqc.fsq_packet.data = FsqInfo(fs, fpath, desc, random.choice(list(FsqStorageDest)))

            fsq_packet_packed = struct.pack(PackUnpackFormat.OPEN,
                                            self.fsqc.fsq_packet.ver,
                                            self.fsqc.fsq_packet.error.rc,
                                            self.fsqc.fsq_packet.error.strerror,
                                            self.fsqc.fsq_packet.state,
                                            self.fsqc.fsq_packet.data.fs,
                                            self.fsqc.fsq_packet.data.fpath,
                                            self.fsqc.fsq_packet.data.desc,
                                            self.fsqc.fsq_packet.data.fsq_storage_dest)

            self.assertEqual(len(fsq_packet_packed), FSQ_PACKET_LENGTH)
            fsq_packet_unpacked = struct.unpack(PackUnpackFormat.OPEN, fsq_packet_packed)
            fsq_packet_restored = FsqPacket(ver = fsq_packet_unpacked[0],
                                            error = FsqError(rc = fsq_packet_unpacked[1],
                                                             strerror = fsq_packet_unpacked[2].decode('ascii').strip('\x00').encode('ascii')),
                                            state = fsq_packet_unpacked[3],
                                            data = FsqInfo(fsq_packet_unpacked[4].decode('ascii').strip('\x00').encode('ascii'),
                                                           fsq_packet_unpacked[5].decode('ascii').strip('\x00').encode('ascii'),
                                                           fsq_packet_unpacked[6].decode('ascii').strip('\x00').encode('ascii'),
                                                           fsq_packet_unpacked[7]))

            self.assertEqual(self.fsqc.fsq_packet, fsq_packet_restored)

    def test_packet_write(self):
        for i in range(0, NUM_REPETITIONS):
            size = 2**64 - 1 if i == 0 else random.randint(0x1, 0xFFFFFFFFFF)
            self.fsqc.fsq_packet.error = FsqError(rc=random.randint(0x0, 0xFF),
                                                  strerror=generate_random_ascii(FSQ_MAX_ERRMSG_LENGTH))
            self.fsqc.fsq_packet.state = FsqProtocolState.FSQ_DATA
            self.fsqc.fsq_packet.data = FsqData(size)

            fsq_packet_packed = struct.pack(PackUnpackFormat.DATA,
                                            self.fsqc.fsq_packet.ver,
                                            self.fsqc.fsq_packet.error.rc,
                                            self.fsqc.fsq_packet.error.strerror,
                                            self.fsqc.fsq_packet.state,
                                            self.fsqc.fsq_packet.data.size)

            self.assertEqual(len(fsq_packet_packed), FSQ_PACKET_LENGTH)
            fsq_packet_unpacked = struct.unpack(PackUnpackFormat.DATA, fsq_packet_packed)
            fsq_packet_restored = FsqPacket(ver=fsq_packet_unpacked[0],
                                            error=FsqError(rc=fsq_packet_unpacked[1],
                                                           strerror=fsq_packet_unpacked[2].decode('ascii').strip('\x00').encode('ascii')),
                                            state=fsq_packet_unpacked[3],
                                            data=FsqData(fsq_packet_unpacked[4]))


            self.assertEqual(self.fsqc.fsq_packet, fsq_packet_restored)

    def test_packet_close(self):
        for _ in range(0, NUM_REPETITIONS):
            self.fsqc.fsq_packet.error = FsqError(rc=random.randint(0x0, 0xFF),
                                                  strerror=generate_random_ascii(FSQ_MAX_ERRMSG_LENGTH))
            self.fsqc.fsq_packet.state = FsqProtocolState.FSQ_CLOSE

            fsq_packet_packed = struct.pack(PackUnpackFormat.CLOSE,
                                            self.fsqc.fsq_packet.ver,
                                            self.fsqc.fsq_packet.error.rc,
                                            self.fsqc.fsq_packet.error.strerror,
                                            self.fsqc.fsq_packet.state)

            self.assertEqual(len(fsq_packet_packed), FSQ_PACKET_LENGTH)
            fsq_packet_unpacked = struct.unpack(PackUnpackFormat.CLOSE, fsq_packet_packed)
            fsq_packet_restored = FsqPacket(ver=fsq_packet_unpacked[0],
                                            error=FsqError(rc=fsq_packet_unpacked[1],
                                                           strerror=fsq_packet_unpacked[2].decode('ascii').strip('\x00').encode('ascii')),
                                            state=fsq_packet_unpacked[3])

            self.assertEqual(self.fsqc.fsq_packet, fsq_packet_restored)

    def test_packet_disconnect(self):
        for _ in range(0, NUM_REPETITIONS):
            self.fsqc.fsq_packet.error = FsqError(rc=random.randint(0x0, 0xFF),
                                                  strerror=generate_random_ascii(FSQ_MAX_ERRMSG_LENGTH))
            self.fsqc.fsq_packet.state = FsqProtocolState.FSQ_DISCONNECT

            fsq_packet_packed = struct.pack(PackUnpackFormat.DISCONNECT,
                                            self.fsqc.fsq_packet.ver,
                                            self.fsqc.fsq_packet.error.rc,
                                            self.fsqc.fsq_packet.error.strerror,
                                            self.fsqc.fsq_packet.state)

            self.assertEqual(len(fsq_packet_packed), FSQ_PACKET_LENGTH)
            fsq_packet_unpacked = struct.unpack(PackUnpackFormat.DISCONNECT, fsq_packet_packed)
            fsq_packet_restored = FsqPacket(ver=fsq_packet_unpacked[0],
                                            error=FsqError(rc=fsq_packet_unpacked[1],
                                                           strerror=fsq_packet_unpacked[2].decode('ascii').strip('\x00').encode('ascii')),
                                            state=fsq_packet_unpacked[3])

            self.assertEqual(self.fsqc.fsq_packet, fsq_packet_restored)

    @unittest.skipIf(not hasattr(unittest.TestCase, 'with_data_write'),
                     'Skipping test with data write')
    def test_data_write(self):
        fs = '/lustre'
        fpath = fs + '/fsqpy/test/'
        fpaths_crc32 = []
        # 1B, 1KiB, 1MiB, 1GiB, 2GiB, 8GiB
        buffer_sizes = [1, 1024, 1024 * 1024, 1024 * 1024 * 1024, 2 * 1024 * 1024 * 1024, 8 * 1024 * 1024 * 1024]

        # Random buffer sizes.
        buffer_sizes.extend([random.randint(1, 0xFFFFFF) for _ in range(100)])
        
        self.fsqc.connect(node='polaris', password='polaris', hostname='localhost', port=7625)
        for buf_size in buffer_sizes:
            fpath = fs + '/fsqpy/test/' + generate_random_ascii(32).decode('ascii')
            self.fsqc.open(fs, fpath, '', dest=FsqStorageDest.FSQ_STORAGE_LOCAL)
            print(f'creating random buffer of size: {buf_size}')
            random_buffer = os.urandom(buf_size)
            print(f'done random buffer of size: {buf_size}')
            print(f'calculating crc32 random buffer of size: {buf_size}')
            crc32_value = zlib.crc32(random_buffer)
            print(f'done crc32 random buffer of size: {buf_size}')
            self.fsqc.write(random_buffer, buf_size)
            self.fsqc.close()
            fpaths_crc32.append((fpath, crc32_value))
        self.fsqc.disconnect()

        modified_fpaths_crc32 = [(filename.replace('/lustre', '/tmp/fsq', 1), size) for filename, size in fpaths_crc32]
        for fpath_crc32 in modified_fpaths_crc32:
            print(fpath_crc32)
            with open(fpath_crc32[0], 'rb') as f:
                buffer = f.read()
                crc32_value = zlib.crc32(buffer)
                self.assertEqual(fpath_crc32[1], crc32_value)

if __name__ == '__main__':
    unittest.main()
