import socket
import datetime
from threading import Thread


DEFAULT_PROXY_IP = '127.0.0.1'
DEFAULT_PROXY_PORT = 8888
SESSION_KEY_LEN = 16    # 2857942574656970690381479936 variants of session_key required to brute force it


class ProxyServer:
    def __init__(self, proxy_ip, proxy_port):
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

    def send(self, data):
        self.sock.send(bytes(data.encode()))

    def get_updates(self):
        updates = self.updates[:]   # copy list, cause I will clear it up
        self.updates = []

        return updates

    def updates_listener(self):
        while True:
            data = self.sock.recv(8192)

            session_key = data[:SESSION_KEY_LEN]
            packet = data[SESSION_KEY_LEN:]

            self.updates += [[session_key, packet]]


class RequestsDistributor:
    def __init__(self, distribution_map):
        self.dmap = distribution_map

    def handle(self, request_type):
        pass
