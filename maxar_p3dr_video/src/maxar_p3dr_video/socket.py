from __future__ import annotations  # noqa

import select
import socket
import struct


def create_and_connect(host: str, port: int) -> socket.socket:
    """
    Create and connect a TCP socket to the given host and port. The
    returned socket must be closed when done.

    Parameters:
        host: The target host.
        port: The target port number.

    Returns:
        The socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.setblocking(0)

    return sock


def receive_payload(sock: socket.socket) -> bytearray:
    """
    Receive payload from the socket by reading size tagged data.

    Parameters:
        sock: The socket to receive from.

    Returns:
        Bytearray with the payload.
    """
    return _read_bytes(sock, _read_size_tag(sock))


def send_payload(sock: socket.socket, payload: bytearray) -> None:
    """
    Write the payload to the socket as size tagged data.

    Parameters:
        socket: The socket to use for sending.
        payload: The payload data.
    """
    size_tag = struct.pack('>I', len(payload))
    sock.sendall(size_tag + payload)


def _read_bytes(sock: socket.socket, size: int) -> bytearray:
    have_data = select.select([sock], [], [], 30.0)
    if have_data[0]:
        received = 0
        payload = bytearray()
        while received < size:
            payload += sock.recv(size - received)
            received = len(payload)

        return payload
    else:
        raise TimeoutError('Socket select timeout')


def _read_size_tag(sock: socket.socket) -> int:
    size_tag = _read_bytes(sock, 4)
    return struct.unpack('>I', size_tag)[0]
