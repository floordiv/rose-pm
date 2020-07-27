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