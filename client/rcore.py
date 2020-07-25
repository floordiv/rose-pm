import json
import socket


DEFAULT_PM_ADDR = ('127.0.0.1', 8888)


class Session:
    def __init__(self, pm_addr=DEFAULT_PM_ADDR):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(pm_addr)

        self.args_for_rtypes = {
            'get-users': (),
            'get-repos': ('login',),
            'get-versions': ('login', 'repo'),
            'get-version': ('login', 'repo', 'version'),
            'repo-exists': ('login', 'repo'),
            'version-exists': ('login', 'repo', 'version'),
            'user-exists': ('login',),
            'get-version-hash': ('login', 'repo', 'version')
        }

    def request(self, rtype, wait_response=True, **payload):
        assert rtype in self.args_for_rtypes

        payload = self.validate_args(rtype, payload)

        if payload is False:    # just if not payload won't work, cause an empty list (possible variant) is False, too
            raise UserWarning('invalid payload')

        self.sock.send(json.dumps({'type': rtype, 'payload': payload}).encode())

        if wait_response:   # this is kinda get-request
            response = json.loads(self.sock.recv(1024).decode())

            return response

    def validate_args(self, rtype, args):
        final_payload = []

        for arg in self.args_for_rtypes[rtype]:
            if arg not in args:
                return False

            final_payload.append(args[arg])

        return final_payload

    def __del__(self):
        self.sock.close()
