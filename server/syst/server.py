import json
import socket
import inspect
import datetime
from time import sleep
from threading import Thread
from sys import exit as abort  # грех
from traceback import format_exc

import syst.repo as repo


DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 8888


class RequestsDistributor:
    def __init__(self, distribution_map):
        self.dmap = distribution_map

    def handle(self, conn, request):
        """
        @type conn: socket.socket
        @type request: dict
        """

        rtype = request['type']
        client_ip, client_port = conn.getpeername()

        if rtype not in self.dmap:
            return conn.send(json.dumps({'type': 'fail', 'desc': 'invalid-request-type'}).encode())

        try:
            func = self.dmap[rtype]
            args = request['payload']

            if list(inspect.signature(func).parameters)[0] == 'conn':
                args.insert(0, conn)

            data = func(*args)

            if data is not None:
                conn.send(json.dumps({'type': 'succ', 'data': data}).encode())
        except (OSError, BrokenPipeError, ConnectionResetError):
            conn.close()
            print(f'[{datetime.datetime.now()}] [MAINSERVER] Disconnected: {client_ip}:{client_port}')
        except Exception as exc:
            print(format_exc())

            conn.send(json.dumps({'type': 'fail', 'desc': str(exc)}).encode())


class MainServer:
    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_PORT):
        self.ip, self.port = ip, port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.updates = []

    def init(self):
        try:
            self.sock.bind((self.ip, self.port))
            self.sock.listen(0)
        except OSError:
            print(f'[{datetime.datetime.now()}] [MAINSERVER] Failed to init server: address already in use')
            abort(1)

    def start(self):
        Thread(target=self.connections_listener).start()
        print(f'[{datetime.datetime.now()}] [MAINSERVER] Successfully initialized and started on {self.ip}:{self.port}')

    def connections_listener(self):
        while True:
            conn, addr = self.sock.accept()

            print(f'[{datetime.datetime.now()}] [MAINSERVER] New connection: {addr[0]}:{addr[1]}')
            Thread(target=self.connections_handler, args=(conn, addr)).start()

    def connections_handler(self, conn, addr):
        try:
            while True:
                data = conn.recv(2048)

                try:
                    decoded = data.decode()

                    if not decoded:
                        raise OSError

                    jsonified = json.loads(decoded)

                    if 'type' not in jsonified or 'payload' not in jsonified:
                        raise json.JSONDecodeError
                except json.JSONDecodeError:
                    conn.send(json.dumps({'type': 'fail', 'desc': 'bad-request'}).encode())
                    continue

                self.updates.append([conn, jsonified])
        except (OSError, BrokenPipeError, ConnectionResetError):
            # print(f'[{datetime.datetime.now()}] [MAINSERVER] Disconnected: {addr[0]}:{addr[1]}')
            conn.close()

    def get_updates(self):
        while not len(self.updates): sleep(0.1)  # to avoid a ka-boom of the server

        updates = self.updates[:]   # copy list
        self.updates = []

        return updates

    def __del__(self):
        print(f'[{datetime.datetime.now()}] [MAINSERVER] Stopping...')
        self.sock.close()


def worker(mainserver=None, requests_handler=None, dmap=None):
    if dmap is None:
        dmap = {
            'get-users': repo.get_users,
            'get-repos': repo.get_repos,
            'get-versions': repo.get_versions,
            'get-version': repo.get_version,
            'repo-exists': repo.exists,
            'version-exists': repo.version_exists,
            'user-exists': repo.user_exists,
            'get-version-hash': repo.gethash,
            'download': repo.download,
        }

    if requests_handler is None:
        requests_handler = RequestsDistributor(dmap)
    if mainserver is None:
        mainserver = MainServer()
        mainserver.init()
        mainserver.start()

    while True:
        updates = mainserver.get_updates()

        for conn, request in updates:
            requests_handler.handle(conn, request)
