import json


class Transmission:
    def __init__(self, conn, filename, chunk_size=1024):
        self.conn = conn
        self.filename = filename
        self.chunk_size = chunk_size

    def start(self):
        with open(self.filename, 'rb') as file:
            chunks = list(iter(lambda: file.read(self.chunk_size), b''))

        self.conn.send(json.dumps(
            {'type': 'trnsmsn-init', 'packets': len(chunks), 'file': self.filename, 'chunk': self.chunk_size}
                                  ).encode())

        for chunk in chunks:
            self.conn.send(chunk)
