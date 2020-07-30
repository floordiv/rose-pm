import json
import socket


DEFAULT_PM_ADDR = ('127.0.0.1', 8888)


class Session:
    def __init__(self, pm_addr=DEFAULT_PM_ADDR):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(pm_addr)

        self.args_for_rtypes = {
            'get-users':            (),
            'get-repos':            ('login',),
            'get-versions':         ('login', 'repo'),
            'get-version':          ('login', 'repo', 'version'),
            'repo-exists':          ('login', 'repo'),
            'version-exists':       ('login', 'repo', 'version'),
            'user-exists':          ('login',),
            'get-version-hash':     ('login', 'repo', 'version'),
            'get-newest-version':   ('login', 'repo'),
            'download':             ('login', 'repo', 'version')
        }

    def request(self, rtype, wait_response=True, direct_api_call=False, **payload):
        assert rtype in self.args_for_rtypes

        payload = self.validate_args(rtype, payload)

        if payload is False and not direct_api_call:  # just if not payload won't work, cause an empty list (possible variant) is False, too
            raise UserWarning('invalid payload')

        self.sock.send(json.dumps({'type': rtype, 'payload': payload}).encode())

        if wait_response:
            source = b''

            # this may be ugly-looking, but if we don't do this,
            # we'll have troubles with big packets receiving
            # for example, receiving huge repos' hashes
            while source.count(b'|') < 2:
                source += self.sock.recv(8)

            next_packet_len = int(source[1:-1])
            self.sock.send(b'ok')

            # we received packet's length, now - it's time to receive our packet
            raw_response = b''

            while len(raw_response) < next_packet_len:
                raw_response += self.sock.recv(1024)

            response = json.loads(raw_response.decode())
            return response

    def validate_args(self, rtype, args):
        final_payload = []

        for arg in self.args_for_rtypes[rtype]:
            if arg not in args:
                return False

            final_payload.append(args[arg])

        return final_payload

    def get_sock(self):
        return self.sock

    def __del__(self):
        self.sock.close()
