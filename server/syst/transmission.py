import os
import json
from time import sleep
from datetime import datetime


class Transmission:
    def __init__(self, conn, filename, chunk_size=1024):
        self.conn = conn
        self.filename = filename
        self.chunk_size = chunk_size

    def start(self):
        print('[TRANSMISSION] Started')

        with open(self.filename, 'rb') as file:
            chunks = list(iter(lambda: file.read(self.chunk_size), b''))

        sleep(0.5)

        self.conn.send(json.dumps(
            {'type': 'trnsmsn-init',
             'packets': len(chunks),
             'file': os.path.basename(self.filename),
             'chunk': self.chunk_size}
                                  ).encode())

        sleep(0.5)

        try:
            for chunk_index, chunk in enumerate(chunks, start=1):
                self.conn.send(chunk)
                print('[TRANSMISSION] Sent', chunk_index, 'chunks of', len(chunks))
            print('[TRANSMISSION] Completed')
        except OSError:
            return
