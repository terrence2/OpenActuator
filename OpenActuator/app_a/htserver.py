import select
import ure
import usocket
from errors import RestartError


class HttpServer:
    """
    A single-threaded, single-tenant HTTP/1 server. We only expect one person to talk to us
    at once, so it doesn't make sense to design for concurrency.

    However, we may still need to do output (e.g. for a button press) while being talked at,
    so this does go as far as using non-blocking I/O and polling for input so that we can
    support full-duplex operation.
    """
    def __init__(self, poll, routes, config):
        self.status_map = {
            200: "OK",
            404: "Not Found",
            503: "Service Unavailable"
        }
        self.routes = routes

        addr_info = usocket.getaddrinfo(config.get('address', '0.0.0.0'), config.get('port', 80))
        bind_addr = addr_info[0][-1]

        self.listen_socket = usocket.socket()
        self.listen_socket.setblocking(False)
        self.listen_socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        self.listen_socket.bind(bind_addr)
        self.listen_socket.listen(3)
        poll.register(self.listen_socket, select.POLLIN | select.POLLERR)
        print("Started HTTPS server on {}", bind_addr)

        self.clients = []

    def is_same_socket(self, maybe_socket, socket):
        # uPython poll returns the actual socket object, whereas CPython poll returns the fd int.
        if isinstance(maybe_socket, int):
            if maybe_socket != socket.fileno():
                return False
        else:
            if maybe_socket != socket:
                return False
        return True

    def handle_ready_socket(self, poller, socket, event):
        if self.is_same_socket(socket, self.listen_socket):
            return self.handle_new_connection(poller, event)

        for handler in self.clients:
            if self.is_same_socket(socket, handler.socket):
                if not handler.handle_client_data(poller, event):
                    return self.clients.remove(handler)

    def handle_new_connection(self, poller, event):
        if event == select.POLLERR:
            raise RestartError("at handle_ready_sock")

        client_socket, client_addr = self.listen_socket.accept()
        print("Got new connection from: {}".format(client_addr))

        self.clients.append(HttpClientHandler(poller, self, client_socket))

    def find_route(self, method: str, path: str):
        for route in self.routes:
            if route[0] != method.upper():
                continue
            elif route[1] == path:
                return route[3], []
            else:
                try:
                    matches = route[1].match(path)
                    args = []
                    for i in range(route[2]):
                        args.append(matches.group(i + 1))
                    return route[3], args
                except AttributeError:
                    continue
        return self._handle_404, []

    def _handle_404(self):
        return 404, [], ""


class HttpClientHandler:
    def __init__(self, poller, server, socket):
        self.server = server
        self.socket = socket
        self.socket.setblocking(False)
        poller.register(self.socket, select.POLLIN | select.POLLERR)

        self.phase = 'read_status'
        self.instream = ''
        self.outstream = b''

        self.method = None
        self.path = None
        self.content_length = 0
        self.body = None

    def handle_client_data(self, poller, event):
        if event == select.POLLERR:
            raise RestartError("at handle_ready_sock")

        if self.phase.startswith('read'):
            # TODO: use readinto when available
            raw = self.socket.recv(1024)
            assert raw
            self.instream += str(raw, 'ascii')

            if self.phase == 'read_status':
                if '\r\n' in self.instream:
                    offset = self.instream.find('\r\n')
                    request_line = self.instream[:offset]
                    self.instream = self.instream[offset + 2:]
                    self.method, self.path, _v = request_line.split()
                    self.phase = 'read_headers'

            if self.phase == 'read_headers':
                while '\r\n' in self.instream:
                    offset = self.instream.find('\r\n')
                    header_line = self.instream[:offset].strip()
                    self.instream = self.instream[offset + 2:]
                    if header_line:
                        header, _, value = header_line.partition(':')
                        if header.strip().lower() == 'content-length':
                            self.content_length = int(value.strip())
                    else:
                        self.phase = 'read_body'

            if self.phase == 'read_body':
                if len(self.instream) >= self.content_length:
                    # We've already read in this frame, so wait for the next loop
                    # before processing the body. To do this we switch the socket
                    # into write mode so that the poller will mark us as ready in
                    # every frame until we actually start writing.
                    poller.unregister(self.socket)
                    poller.register(self.socket, select.POLLOUT | select.POLLERR)
                    self.phase = 'handle_request'

        elif self.phase == 'handle_request':
            handler, args = self.server.find_route(self.method, self.path)
            status, headers, body = handler(*args)
            status_message = self.server.status_map.get(status, 'Unknown Code')
            body = bytes(body, 'ascii')
            self.outstream = bytes("HTTP/1.0 {} {}\r\n".format(status, status_message), 'ascii')
            for key, value in headers:
                self.outstream += bytes("{}: {}\r\n".format(key, value), 'ascii')
            self.outstream += b"\r\n"
            self.outstream += body
            self.phase = 'write'

        elif self.phase == 'write':
            sent_bytes = self.socket.send(self.outstream)
            if sent_bytes == len(self.outstream):
                poller.unregister(self.socket)
                self.socket.close()
                return False
            self.outstream = self.outstream[sent_bytes:]

        return True

