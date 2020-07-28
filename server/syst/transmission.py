import os
import json
import time
import shutil
import tarfile
from socket import timeout
from datetime import datetime


"""
You may ask me, why did I copypaste the same module to the client, and server folders?

Cause I don't wanna distribute Rose with server inside, server and client are independent packages
"""


class UploadTransmission:
    def __init__(self, conn, filename, chunk_size=1024):
        self.conn = conn
        self.filename = filename
        self.chunk_size = chunk_size

    def start(self):
        print(f'[{datetime.now()}] [TRANSMISSION] Started')

        with open(self.filename, 'rb') as file:
            chunks = list(iter(lambda: file.read(self.chunk_size), b''))

        chunks_count = len(chunks)

        self.conn.send(json.dumps(
            {'type': 'trnsmsn-init',
             'packets': chunks_count,
             'file': os.path.basename(self.filename),
             'chunk': self.chunk_size}
        ).encode())

        self.conn.recv(10)

        for chunk_index, chunk in enumerate(chunks, start=1):
            self.conn.send(chunk)
            print(f'[{datetime.now()}] [TRANSMISSION] Sent', chunk_index, 'chunks of', chunks_count)
        print(f'[{datetime.now()}] [TRANSMISSION] Completed')


class DownloadTransmission:
    def __init__(self, session, author, repo, version, dest='installed'):
        if not os.path.exists(dest):
            os.mkdir(dest)

        self.sock = session.get_sock()
        self.dest = dest
        self.repo = repo
        self.version = version
        self.author = author
        self.packets = None
        self.filename = 'unknown.tar.gz'
        self.chunksize = 1024

    def start(self):
        self.sock.settimeout(3)

        try:
            data = self.sock.recv(1024)
        except timeout:
            print('[ROSE] Server does not responds')
            return

        init_packet = json.loads(data.decode())

        if init_packet['type'] == 'trnsmsn-init':
            self.packets = init_packet['packets']
            self.filename = init_packet['file']
            self.chunksize = init_packet['chunk']

            self.sock.send(b'ok')
        else:
            print(init_packet)
            print('[ROSE] Transmission failed: did not receive initial packet')
            return

        with open(os.path.join(self.dest, self.filename), 'wb') as tar_file:
            for i in range(self.packets):
                source = self.sock.recv(self.chunksize)
                tar_file.write(source)

                print('[ROSE] Received', i + 1, 'packets of', self.packets)
            print('[ROSE] Transmission completed')

        self.unpack_tar()

    def unpack_tar(self):
        if not os.path.exists(self.dest):
            os.mkdir(self.dest)

        tar = tarfile.open(os.path.join(self.dest, self.filename))
        tar.extractall(self.dest)

        if not os.path.exists(self.dest + '/' + self.repo):
            os.mkdir(self.dest + '/' + self.repo)

        shutil.move(f'{self.dest}/repos/{self.author}/{self.repo}/{self.version}', self.dest)

        os.rename(self.dest + '/' + self.version, self.dest + '/' + self.repo)

        shutil.rmtree(self.dest + '/repos')
        os.remove(os.path.join(self.dest, self.filename))

        version_info = {
            'version': self.version,
            'author': self.author,
            'download-date': time.time()
        }

        with open(self.dest + '/' + self.repo + '/.version', 'w') as version_info_file:
            json.dump(version_info, version_info_file)

        print('[ROSE] Installed')

    def rm_extension(self, filename, extension):
        return filename[:-len(extension)]
