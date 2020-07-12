import string
import socket
import datetime
from random import choices
from threading import Thread


DEFAULT_INTERNAL_PORT = 8888
DEFAULT_EXTERNAL_PORT = 9999
SESSION_KEY_LEN = 16    # this variable should be synchronized with main server, otherwise - nothing will work


class InternalServer:
    def __init__(self, port=DEFAULT_INTERNAL_PORT, autostart=True):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.bind(('127.0.0.1', port))
        except OSError:
            print(f'[{datetime.datetime.now()}] [LOCAL-SERVER] Failed to start on 127.0.0.1:{port}: already in use')

        sock.listen(1)  # currently, only one server is available. Loadbalancer functions will be added later
        self.sock = sock
        self.response_pool = []

    def start(self):
        Thread(target=self.start_on_conn).start()

    def start_on_conn(self):
        print(f'[{datetime.datetime.now()}] [LOCAL-SERVER] Waiting for a main-server connection...')
        conn, addr = self.sock.accept()
        print(f'[{datetime.datetime.now()}] [LOCAL-SERVER] Successfully connected main-server: {addr[0]}:{addr[1]}')

    def listener(self):
        while True:
            response = self.sock.recv(8192).decode()
            session_key = response[:SESSION_KEY_LEN]
            response_body = response[SESSION_KEY_LEN:]

            self.response_pool += [[session_key, response_body]]

    def request(self, session_key, packet):
        packet = session_key + packet
        self.sock.send(packet.encode())

    def get_responses(self):
        responses = self.response_pool[:]
        self.response_pool = []

        return responses


class ExternalServer:
    def __init__(self, port=DEFAULT_EXTERNAL_PORT, internal_server=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if not internal_server:
            internal_server = InternalServer()

        try:
            sock.bind(('127.0.0.1', port))
        except OSError:
            print(f'[{datetime.datetime.now()}] [EXTERNAL-SERVER] Failed to start on 127.0.0.1:{port}: already in use')

        sock.listen(0)
        self.sock = sock
        self.internal_server = internal_server
        self.sessions = {}

    def start(self):
        Thread(target=self.connlistener).start()

    def connlistener(self):
        while True:
            conn, addr = self.sock.accept()

            session_key = self.generate_session_key()
            self.sessions[session_key] = conn

            Thread(target=self.conn_handler, args=(conn, addr, session_key)).start()

    def conn_handler(self, conn, addr, session_key):
        addr = addr[0] + ':' + str(addr[1])

        try:
            while True:
                data = conn.recv(8192).decode()

                self.internal_server.request(session_key, data)
        except BrokenPipeError:
            print(f'[{datetime.datetime.now()}] [EXTERNAL-SERVER:connection] {addr}: disconnected')

    def internal_requests_worker(self):
        while True:
            requests = self.internal_server.get_responses()

            for session_key, request_body in requests:
                self.sessions[session_key].send(request_body)

    def generate_session_key(self):
        return ''.join(choices(string.ascii_letters, k=SESSION_KEY_LEN))
