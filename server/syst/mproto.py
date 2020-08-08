import socket
import struct


def sendmsg(conn, data):
    """
    @type conn: socket.socket
    @type data: str
    """

    bytelike_source = bytes(data)
    msg_len = struct.pack('>I', len(bytelike_source))

    conn.send(msg_len)
    conn.recv(4)    # wait for client approving. 4 bytes is enough (we don't need too much)
    conn.send(bytelike_source)


def recvmsg(conn):
    """
    @type conn: socket.socket
    """

    msg_len = struct.unpack('>I', conn.recv(4))[0]  # [0] cause struct.unpack returns tuple
    conn.send(b'ok')    # we received and processed new message, so, let's approve it for server

    # it's time to receive our message!
    received_message = b''

    while len(received_message) < msg_len:
        received_message += conn.recv(msg_len - len(received_message))

    return received_message   # I don't care, decode it by yourself.
