import os
import sys
import json
import time
import shutil
import tarfile
import hashlib
from socket import timeout
from datetime import datetime


"""
You may ask me, why did I copypaste the same module to the client, and server folders?

Cause I don't wanna distribute Rose with server inside, server and client are independent packages
"""


class UploadTransmission:
    def __init__(self, conn, filename, chunk_size=2048):
        self.conn = conn
        self.addr = conn.getpeername()
        self.filename = filename
        self.chunk_size = chunk_size

    def start(self):
        print(f'[{datetime.now()}] [TRANSMISSION] Started: {self.addr[0]}:{self.addr[1]}')

        with open(self.filename, 'rb') as file:
            chunks = list(iter(lambda: file.read(self.chunk_size), b''))

        chunks_count = len(chunks)
        total_bytes = (self.chunk_size * (chunks_count - 1)) + len(chunks[-1])

        self.conn.send(json.dumps(
            {'type': 'trnsmsn-init',
             'bytes': total_bytes,
             'file': os.path.basename(self.filename),
             'chunk': self.chunk_size}
        ).encode())

        data = self.conn.recv(10)

        if not data:  # client closed connection
            raise OSError

        for chunk_index, chunk in enumerate(chunks, start=1):
            self.conn.send(chunk)

        print(f'[{datetime.now()}] [TRANSMISSION] Completed: {self.addr[0]}:{self.addr[1]}')


class DownloadTransmission:
    def __init__(self, conn, author, repo, version):
        self.sock = conn
        self.repo = repo
        self.version = version
        self.author = author

        self.dest = 'repos'
        self.bytes = None
        self.filename = version + '.tar.gz'
        self.chunksize = 2048

    def start(self):
        self.sock.settimeout(3)

        try:
            data = self.sock.recv(1024)
        except timeout:
            print(f'[{datetime.now()}] [DOWNLOAD-TRANSMISSION] Client does not responds')
            return

        init_packet = json.loads(data.decode())

        if init_packet['type'] == 'trnsmsn-init':
            self.bytes = init_packet['bytes']
            self.filename = init_packet['file']
            self.chunksize = init_packet['chunk']

            self.sock.send(b'ok')
        else:
            print(init_packet)
            print('[ROSE] Transmission failed: did not receive initial packet')
            return

        with open('repos/' + self.version, 'wb') as tar_file:
            total_bytes_received = 0

            while total_bytes_received < self.bytes:
                source = self.sock.recv(self.bytes - total_bytes_received)
                tar_file.write(source)
                total_bytes_received += len(source)

            print(f'[{datetime.now()}] [DOWNLOAD-TRANSMISSION] Completed')

    def install(self):
        ...
