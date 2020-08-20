import os
import json
import socket
import inspect
import datetime
from time import sleep
from threading import Thread
from sys import exit as abort  # грех
from traceback import format_exc

import syst.repo as repo
import syst.mproto as mproto


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
            return mproto.sendmsg(conn, json.dumps({'type': 'fail', 'data': 'invalid-request-type'}).encode())

        try:
            func = self.dmap[rtype]
            args = request['payload']

            if list(inspect.signature(func).parameters)[0] == 'conn':
                args.insert(0, conn)

            data = func(*args)

            if data is not None:
                response = json.dumps({'type': 'succ', 'data': data}).encode()
                mproto.sendmsg(conn, response)
        except (OSError, BrokenPipeError, ConnectionResetError):
            conn.close()
            print(f'[{datetime.datetime.now()}] [MAINSERVER] Disconnected: {client_ip}:{client_port}')
        except AssertionError:
            mproto.sendmsg(conn, json.dumps({'type': 'fail', 'data': 'bad-data'}).encode())
        except Exception as exc:
            print(format_exc())
            mproto.sendmsg(conn, json.dumps({'type': 'fail', 'data': str(exc)}).encode())


class MainServer:
    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_PORT,
                 rdistributor=None, dmap=None):
        self.ip, self.port = ip, port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if dmap is None:
            self.dmap = {
                'get-users': repo.get_users,
                'get-repos': repo.get_repos,
                'get-versions': repo.get_versions,
                'get-version': repo.get_version,
                'repo-exists': repo.exists,
                'version-exists': repo.version_exists,
                'user-exists': repo.user_exists,
                'get-version-hash': repo.gethash,
                'get-newest-version': repo.get_newest_version,
                'download': repo.download,
            }

        if rdistributor is None:
            self.distributor = RequestsDistributor(self.dmap)

    def init(self):
        try:
            self.sock.bind((self.ip, self.port))
            self.sock.listen(0)
        except OSError:
            print(f'[{datetime.datetime.now()}] [MAINSERVER] Failed to init server: address already in use')
            abort(1)

    def start(self, threaded=True):
        print(f'[{datetime.datetime.now()}] [MAINSERVER] Successfully initialized and started on {self.ip}:{self.port}')

        if threaded:
            Thread(target=self.connections_listener).start()
        else:
            self.connections_listener()

    def connections_listener(self):
        while True:
            conn, addr = self.sock.accept()

            print(f'[{datetime.datetime.now()}] [MAINSERVER] New connection: {addr[0]}:{addr[1]}')
            Thread(target=self.connections_handler, args=(conn, addr)).start()

    def connections_handler(self, conn, addr):
        try:
            while True:
                data = mproto.recvmsg(conn)

                if not data:
                    raise ConnectionResetError

                try:
                    decoded = data.decode()

                    if not decoded:
                        raise OSError

                    jsonified = json.loads(decoded)

                    if 'type' not in jsonified or 'payload' not in jsonified:
                        raise json.JSONDecodeError
                except json.JSONDecodeError:
                    mproto.sendmsg(conn, json.dumps({'type': 'fail', 'data': 'bad-request'}).encode())
                    continue

                self.distributor.handle(conn, jsonified)
        except (OSError, BrokenPipeError, ConnectionResetError):
            print(f'[{datetime.datetime.now()}] [MAINSERVER] Disconnected: {addr[0]}:{addr[1]}')
            conn.close()

    def stop(self):
        print(f'\n[{datetime.datetime.now()}] [MAINSERVER] Stopping...')
        self.sock.close()

    def __del__(self):
        self.stop()
