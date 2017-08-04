import os
import sys
sys.path.append(os.path.realpath('./OpenActuator/app_a'))
sys.path.append(os.path.realpath('./test/mock'))

if os.path.isfile('LICENSE'):
    os.chdir('./test')
import htserver

import re
import select
import socket
from helpers import threaded


ADDRESS = ('127.0.0.1', 12346)
CONFIG = {"ADDRESS": ADDRESS[0], "port": ADDRESS[1]}


def _drain(sock):
    parts = []
    data = b'----'
    while data != b'':
        data = sock.recv(1024)
        parts.append(data)
    return b''.join(parts)


def test_404_on_no_routes():
    poller = select.poll()
    server = htserver.HttpServer(poller, [], CONFIG)

    def _client(ADDRESS):
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(b"GET /foo HTTP/1.1\r\n\r\n")
        data = _drain(sock)
        assert data == b'HTTP/1.0 404 Not Found\r\n\r\n'

    with threaded(_client, ADDRESS):
        ready = poller.poll(1)
        server.handle_ready_socket(poller, *ready[0])
        ready = poller.poll(1)
        server.handle_ready_socket(poller, *ready[0])


def _200_ok(msg):
    def _inner(*args):
        return 200, [], msg + " ".join(args)
    return _inner


def test_basic_routes():
    poller = select.poll()
    routes = [
        ('GET', '/foo', 0, _200_ok("foo")),
        ('GET', '/bar', 0, _200_ok("bar"))
    ]
    server = htserver.HttpServer(poller, routes, CONFIG)

    def _foo_client(ADDRESS):
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(b"GET /foo HTTP/1.1\r\n\r\n")
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: 3\r\n\r\nfoo'

    def _bar_client(ADDRESS):
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(b"GET /bar HTTP/1.1\r\n\r\n")
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: 3\r\n\r\nbar'

    with threaded(_foo_client, ADDRESS):
        ready = poller.poll(1)
        server.handle_ready_socket(poller, *ready[0])
        ready = poller.poll(1)
        server.handle_ready_socket(poller, *ready[0])

    with threaded(_bar_client, ADDRESS):
        ready = poller.poll(1)
        server.handle_ready_socket(poller, *ready[0])
        ready = poller.poll(1)
        server.handle_ready_socket(poller, *ready[0])


def test_regex_routes():
    poller = select.poll()
    routes = [
        ('GET', re.compile('/foo/(.+)'), 1, _200_ok("")),
        ('GET', re.compile('/bar/(.+)/(.+)/id'), 2, _200_ok(""))
    ]
    server = htserver.HttpServer(poller, routes, CONFIG)

    def _foo_client(ADDRESS):
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(b"GET /foo/my-id HTTP/1.1\r\n\r\n")
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: 5\r\n\r\nmy-id'

    def _bar_client(ADDRESS):
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(b"GET /bar/aaaa/bbbb/id HTTP/1.1\r\n\r\n")
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: 9\r\n\r\naaaa bbbb'

    with threaded(_foo_client, ADDRESS):
        ready = poller.poll(1)
        server.handle_ready_socket(poller, *ready[0])
        ready = poller.poll(1)
        server.handle_ready_socket(poller, *ready[0])

    with threaded(_bar_client, ADDRESS):
        ready = poller.poll(1)
        server.handle_ready_socket(poller, *ready[0])
        ready = poller.poll(1)
        server.handle_ready_socket(poller, *ready[0])
