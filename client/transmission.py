import os
import json
import time
import shutil
import tarfile


class Transmission:
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

        data = self.sock.recv(1024)
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
