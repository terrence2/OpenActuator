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

    finished_client = False

    def _client(ADDRESS):
        nonlocal finished_client
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(b"GET /foo HTTP/1.1\r\n\r\n")
        data = _drain(sock)
        assert data == b'HTTP/1.0 404 Not Found\r\n\r\n'
        finished_client = True

    with threaded(_client, ADDRESS):
        while True:
            ready = poller.poll(1)
            if not ready and not server.clients:
                break
            for info in ready:
                server.handle_ready_socket(poller, *info)

    assert finished_client


def _200_ok(msg):
    def _inner(*args):
        result = msg + " ".join(args)
        return 200, [('Content-Length', str(len(result)))], result
    return _inner


def test_basic_routes():
    poller = select.poll()
    routes = [
        ('GET', '/foo', 0, _200_ok("foo")),
        ('GET', '/bar', 0, _200_ok("bar"))
    ]
    server = htserver.HttpServer(poller, routes, CONFIG)

    finished_clients = 0

    def _foo_client(ADDRESS):
        nonlocal finished_clients
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(b"GET /foo HTTP/1.1\r\n\r\n")
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: 3\r\n\r\nfoo'
        finished_clients += 1

    def _bar_client(ADDRESS):
        nonlocal finished_clients
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(b"GET /bar HTTP/1.1\r\n\r\n")
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: 3\r\n\r\nbar'
        finished_clients += 1

    with threaded(_foo_client, ADDRESS):
        while True:
            ready = poller.poll(1)
            if not ready and not server.clients:
                break
            for info in ready:
                server.handle_ready_socket(poller, *info)

    with threaded(_bar_client, ADDRESS):
        while True:
            ready = poller.poll(1)
            if not ready and not server.clients:
                break
            for info in ready:
                server.handle_ready_socket(poller, *info)

    assert finished_clients == 2


def test_regex_routes():
    poller = select.poll()
    routes = [
        ('GET', re.compile('/foo/(.+)'), 1, _200_ok("")),
        ('GET', re.compile('/bar/(.+)/(.+)/id'), 2, _200_ok(""))
    ]
    server = htserver.HttpServer(poller, routes, CONFIG)

    finished_clients = 0

    def _foo_client(ADDRESS):
        nonlocal finished_clients
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(b"GET /foo/my-id HTTP/1.1\r\n\r\n")
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: 5\r\n\r\nmy-id'
        finished_clients += 1

    def _bar_client(ADDRESS):
        nonlocal finished_clients
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(b"GET /bar/aaaa/bbbb/id HTTP/1.1\r\n\r\n")
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: 9\r\n\r\naaaa bbbb'
        finished_clients += 1

    with threaded(_foo_client, ADDRESS):
        while True:
            ready = poller.poll(1)
            if not ready and not server.clients:
                break
            for info in ready:
                server.handle_ready_socket(poller, *info)

    with threaded(_bar_client, ADDRESS):
        while True:
            ready = poller.poll(1)
            if not ready and not server.clients:
                break
            for info in ready:
                server.handle_ready_socket(poller, *info)

    assert finished_clients == 2


def test_large_response():
    size = 1024 * 1024 * 10

    poller = select.poll()
    routes = [('GET', '/foo', 0, _200_ok("foop" * size))]
    server = htserver.HttpServer(poller, routes, CONFIG)

    finished_clients = 0

    def _foo_client(ADDRESS):
        nonlocal finished_clients
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(b"GET /foo HTTP/1.1\r\n\r\n")
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: {}\r\n\r\n{}'.format(4 * size, 'foop' * size)
        finished_clients += 1

    with threaded(_foo_client, ADDRESS):
        while True:
            ready = poller.poll(1)
            if not ready and not server.clients:
                break
            for info in ready:
                server.handle_ready_socket(poller, *info)

    assert finished_clients == 1


def test_large_request():
    size = 1024

    poller = select.poll()
    routes = [('GET', '/foo', 0, _200_ok("hi"))]
    server = htserver.HttpServer(poller, routes, CONFIG)

    finished_clients = 0

    def _foo_client(ADDRESS):
        nonlocal finished_clients
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(bytes("GET /foo HTTP/1.1\r\nContent-Length: {}\r\n\r\n{}".format(4 * size, 'foop' * size), 'ascii'))
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nhi'
        finished_clients += 1

    with threaded(_foo_client, ADDRESS):
        while True:
            ready = poller.poll(1)
            if not ready and not server.clients:
                break
            for info in ready:
                server.handle_ready_socket(poller, *info)

    assert finished_clients == 1


def test_zero_content_length():
    poller = select.poll()
    routes = [('GET', '/foo', 0, _200_ok("hi"))]
    server = htserver.HttpServer(poller, routes, CONFIG)

    finished_clients = 0

    def _foo_client(ADDRESS):
        nonlocal finished_clients
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(bytes("GET /foo HTTP/1.1\r\nContent-Length: 0\r\n\r\n", 'ascii'))
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nhi'
        finished_clients += 1

    with threaded(_foo_client, ADDRESS):
        while True:
            ready = poller.poll(1)
            if not ready and not server.clients:
                break
            for info in ready:
                server.handle_ready_socket(poller, *info)

    assert finished_clients == 1


def test_large_header():
    size = 1024

    poller = select.poll()
    routes = [('GET', '/foo', 0, _200_ok("hi"))]
    server = htserver.HttpServer(poller, routes, CONFIG)

    finished_clients = 0

    def _foo_client(ADDRESS):
        nonlocal finished_clients
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(bytes("GET /foo HTTP/1.1\r\nX-Custom-Header: {}\r\n\r\n".format('foop' * size), 'ascii'))
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: 2\r\n\r\nhi'
        finished_clients += 1

    with threaded(_foo_client, ADDRESS):
        while True:
            ready = poller.poll(1)
            if not ready and not server.clients:
                break
            for info in ready:
                server.handle_ready_socket(poller, *info)

    assert finished_clients == 1


def test_concurrent_clients():
    read_size = 1024
    write_size = 1024 * 1024 * 10

    poller = select.poll()
    routes = [('GET', '/foo', 0, _200_ok("foop" * write_size))]
    server = htserver.HttpServer(poller, routes, CONFIG)

    import threading
    lock = threading.Lock()
    finished_clients = 0

    def _foo_client(ADDRESS):
        nonlocal finished_clients
        sock = socket.socket()
        sock.setblocking(True)
        sock.connect(ADDRESS)
        sock.send(bytes("GET /foo HTTP/1.1\r\nContent-Length: {}\r\n\r\n{}".format(4 * read_size, 'foop' * read_size), 'ascii'))
        data = _drain(sock)
        assert str(data, 'ascii') == 'HTTP/1.0 200 OK\r\nContent-Length: {}\r\n\r\n{}'.format(4 * write_size, 'foop' * write_size)
        with lock:
            finished_clients += 1

    with threaded(_foo_client, ADDRESS):
        with threaded(_foo_client, ADDRESS):
            with threaded(_foo_client, ADDRESS):
                with threaded(_foo_client, ADDRESS):
                    with threaded(_foo_client, ADDRESS):
                        with threaded(_foo_client, ADDRESS):
                            while True:
                                ready = poller.poll(1)
                                if not ready and not server.clients:
                                    break
                                for info in ready:
                                    server.handle_ready_socket(poller, *info)

    assert finished_clients == 6
