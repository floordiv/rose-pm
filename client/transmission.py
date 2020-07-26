import os
import json
import tarfile


class Transmission:
    def __init__(self, session, dist='installed'):
        if not os.path.exists(dist):
            os.mkdir(dist)

        self.sock = session.get_sock()
        self.dist = dist
        self.packets = None
        self.filename = 'unknown.tar.gz'
        self.chunksize = 1024

    def start(self):
        init_packet = json.loads(self.sock.recv(1024).decode())

        if init_packet['type'] == 'trnsmsn-init':
            self.packets = init_packet['packets']
            self.filename = init_packet['file']
            self.chunksize = init_packet['chunk']

        with open(os.path.join(self.dist, self.filename), 'wb') as tar_file:
            for _ in range(self.packets):
                source = self.sock.recv(self.chunksize)
                tar_file.write(source)
            print('Received')

    def unpack_tar(self, name):
        ...
