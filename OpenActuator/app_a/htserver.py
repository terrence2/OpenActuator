import conf
import time
import select
import usocket
import ussl


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
    def __init__(self, poll):
        addr_info = usocket.getaddrinfo('0.0.0.0', 80)
        bind_addr = addr_info[0][-1]

        time.sleep_ms(100)

        self.listen_socket = usocket.socket()
        self.listen_socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        self.listen_socket.bind(bind_addr)
        self.listen_socket.listen(3)
        poll.register(self.listen_socket, select.POLLIN | select.POLLERR)
        print("Started HTTPS server on {}", bind_addr)

    def handle_ready_socket(self, poll, socket, event):
        if socket == self.listen_socket:
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

            while True:
                line = fp.readline()
                if not line or line == b'\r\n':
                    break
            client_socket.send("HTTP/1.0 200 OK\r\n")
            client_socket.close()

