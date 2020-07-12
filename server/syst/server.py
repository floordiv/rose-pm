import json
import socket
import datetime
from time import sleep
from threading import Thread

import syst.repo as repo


DEFAULT_PROXY_IP = '127.0.0.1'
DEFAULT_PROXY_PORT = 8888
SESSION_KEY_LEN = 16    # 2857942574656970690381479936 variants of session_key required to brute force it


class ProxyServer:
    def __init__(self, proxy_ip=DEFAULT_PROXY_IP, proxy_port=DEFAULT_PROXY_PORT):
        self.proxy_addr = proxy_ip + ':' + str(proxy_port)
        self.updates = []   # [client, data]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((proxy_ip, proxy_port))
            print(f'[{datetime.datetime.now()}] [RUN-SERVER:connecting] Successfully connected to the proxy-server: {self.proxy_addr}')
            self.sock = sock

            Thread(target=self.updates_listener).start()
        except Exception as exc:
            print(f'[{datetime.datetime.now()}] [RUN-SERVER:connecting] Failed to connect to the proxy-server: {exc}')
            self.sock = None

    def send(self, session_key, data):
        packet = session_key + '|' + json.dumps(data)

        self.sock.send(bytes(packet.encode()))

    def get_updates(self):
        updates = self.updates[:]   # copy list, cause I will clear it up
        self.updates = []

        return updates

    def updates_listener(self):
        while True:
            try:
                data = self.sock.recv(8192).decode()
            except UnicodeDecodeError:
                continue

            session_key = data[:SESSION_KEY_LEN]

            try:
                packet = json.loads(data[SESSION_KEY_LEN:])

                if 'type' not in packet or 'payload' not in packet:
                    # payload should exist anyway, even if it's an empty list
                    raise json.JSONDecodeError  # I'm too lazy to copypaste code in except block
            except json.JSONDecodeError:
                self.send(session_key, {'type': 'fail', 'desc': 'invalid-data'})
                continue

            self.updates += [[session_key, packet]]


class RequestsDistributor:
    def __init__(self, proxy_server, distribution_map):
        self.pserver = proxy_server
        self.dmap = distribution_map

    def handle(self, session_key, request):
        rtype = request['type']

        if rtype not in self.dmap:
            return self.pserver.send(session_key, {'type': 'fail', 'desc': 'invalid-request-type'})

        try:
            data = self.dmap[rtype](*request['payload'])
            self.pserver.send(session_key, {'type': 'succ', 'data': data})
        except Exception as exc:
            self.pserver.send(session_key, {'type': 'fail', 'desc': str(exc)})


def worker(proxy_server=None, requests_handler=None, dmap=None):
    if dmap is None:
        dmap = {
            'get-users': repo.get_users,
            'get-repos': repo.get_repos,
            'get-versions': repo.get_versions,
            'get-version': repo.get_version,
            'repo-exists': repo.exists,
            'version-exists': repo.version_exists,
            'user-exists': repo.user_exists,
            'get-version-hash': repo.gethash
        }

    if proxy_server is None:
        proxy_server = ProxyServer()
    if requests_handler is None:
        requests_handler = RequestsDistributor(proxy_server, dmap)

    while True:
        updates = proxy_server.get_updates()

        for session_key, request in updates:
            requests_handler.handle(session_key, request)
