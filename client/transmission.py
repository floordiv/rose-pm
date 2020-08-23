import os
import sys
import json
import time
import shutil
import tarfile
from socket import timeout
from datetime import datetime

import mproto


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

        mproto.sendmsg(self.conn, json.dumps(
            {'type': 'trnsmsn-init',
             'bytes': total_bytes,
             'file': os.path.basename(self.filename),
             'chunk': self.chunk_size}).encode())

        for chunk_index, chunk in enumerate(chunks, start=1):
            self.conn.send(chunk)

        print(f'[{datetime.now()}] [TRANSMISSION] Completed: {self.addr[0]}:{self.addr[1]}')


class DownloadTransmission:
    def __init__(self, session, author, repo, version, dest='installed', timeit=False):
        if not os.path.exists(dest):
            os.mkdir(dest)
        if version == '&newest':
            version = session.request('get-newest-version', login=author, repo=repo)

        self.sock = session.get_sock()
        self.dest = dest
        self.repo = repo
        self.version = version
        self.author = author
        self.bytes = None
        self.filename = 'unknown.tar.gz'

        self.timeit = timeit
        self.samples = {
            'KB': 1024,
            'MB': 1048576,
            'GB': 1073741824
        }

    def start(self):
        self.sock.settimeout(5)

        try:
            data = mproto.recvmsg(self.sock)
        except timeout:
            print('[ROSE] Server does not responds')
            return

        init_packet = json.loads(data.decode())

        if init_packet['type'] == 'trnsmsn-init':
            self.bytes = init_packet['bytes']
            self.filename = init_packet['file']
        else:
            print('[ROSE] Transmission failed: did not receive initial packet')
            return

        value, name = self.convert_bytes(self.bytes)

        begin = time.time()

        with open(os.path.join(self.dest, self.filename), 'wb') as tar_file:
            total_bytes_received = 0

            last_output_length = 0

            while total_bytes_received < self.bytes:
                source = self.sock.recv(self.bytes - total_bytes_received)
                tar_file.write(source)
                total_bytes_received += len(source)

                received_value, received_name = self.convert_bytes(total_bytes_received)

                sys.stdout.write('\r' + ' ' * last_output_length)

                text = f'[ROSE] Received {received_value} {received_name} of {value} {name}'
                last_output_length = len(text)

                sys.stdout.write('\r' + text)
                sys.stdout.flush()

            print('\n[ROSE] Transmission completed')

        transmission_end = time.time()

        self.unpack_tar()

        absolute_end = time.time()

        if self.timeit:
            average_download_speed_value, name = self.convert_bytes(self.bytes / (transmission_end - begin))
            print(f'[ROSE] Finished in: {round(absolute_end - begin, 2)} seconds with average download speed:'
                  f' {average_download_speed_value} {name}')

    def unpack_tar(self):
        if not os.path.exists(self.dest):
            os.mkdir(self.dest)

        tar = tarfile.open(os.path.join(self.dest, self.filename))
        tar.extractall(self.dest)

        if not os.path.exists(self.dest + '/' + self.repo):
            os.mkdir(self.dest + '/' + self.repo)

        try:
            shutil.move(f'{self.dest}/repos/{self.author}/{self.repo}/{self.version}', self.dest)
        except shutil.Error:
            shutil.copytree(f'{self.dest}/repos/{self.author}/{self.repo}/{self.version}', self.dest)

        try:
            os.rename(self.dest + '/' + self.version, self.dest + '/' + self.repo)
        except OSError:
            shutil.rmtree(self.dest + '/' + self.repo)
            os.rename(self.dest + '/' + self.version, self.dest + '/' + self.repo)

        shutil.rmtree(self.dest + '/repos')
        os.remove(os.path.join(self.dest, self.filename))

        version_info = {
            'version': self.version,
            'author': self.author,
            'download-date': time.time()
        }

        with open(self.dest + '/' + self.repo + '/.version', 'w') as version_info_file:
            json.dump(version_info, version_info_file, indent=4)

        print('[ROSE] Installed')

    def rm_extension(self, filename, extension):
        return filename[:-len(extension)]

    def convert_bytes(self, source):
        for name, num in list(self.samples.items())[::-1]:
            if source >= num:
                value, name = round(source / num, 2), name
                break
        else:
            value, name = source, 'B'

        return value, name
