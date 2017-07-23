import select
import ure
import usocket


class RestartError(Exception):
    pass


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
        self.listen_socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        self.listen_socket.bind(bind_addr)
        self.listen_socket.listen(3)
        poll.register(self.listen_socket, select.POLLIN | select.POLLERR)
        print("Started HTTPS server on {}", bind_addr)

    def handle_ready_socket(self, socket, event):
        # uPython poll returns the actual socket object, whereas CPython poll returns the fd int.
        if isinstance(socket, int):
            if socket != self.listen_socket.fileno():
                return
        else:
            if socket != self.listen_socket:
                return

        if event == select.POLLERR:
            raise RestartError("at handle_ready_sock")

        client_socket, client_addr = self.listen_socket.accept()
        print("Got new connection from: {}".format(client_addr))

        fp = client_socket.makefile('rwb', 0)
        #self.client_ssl = ussl.wrap_socket(self.client_socket, server_side=True,
        #                                   keyfile=conf.config()['http_server']['keyfile'],
        #                                   certfile=conf.config()['http_server']['certfile'],
        #                                   ca_certs=conf.config()['http_server']['ca_certs'],
        #                                   cert_reqs=0)  # FIXME: ussl.CERT_REQUIRED, once supported on ESP)

        request_line = header_line = str(fp.readline(), 'ascii')
        while header_line and header_line != '\r\n':
            header_line = str(fp.readline(), 'ascii')

        # Dispatch to route.
        method, path, _v = request_line.split()
        handler, args = self.find_route(method, path)
        status, headers, body = handler(*args)
        body = bytes(body, 'ascii')

        status_message = self.status_map.get(status, 'Unknown Code')
        client_socket.send(bytes("HTTP/1.0 {} {}\r\n".format(status, status_message), 'ascii'))

        headers = {}
        if body:
            headers['Content-Length'] = str(len(body))
        for key, value in headers.items():
            client_socket.send(bytes("{}: {}\r\n".format(key, value), 'ascii'))
        client_socket.send(b"\r\n")

        if body:
            client_socket.send(body)

        client_socket.close()

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
