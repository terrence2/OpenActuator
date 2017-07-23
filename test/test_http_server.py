import socket
import ssl

ADDRESS = ('10.0.4.27', 443)


def test_connect():
    sock = socket.socket()
    sock.connect(ADDRESS)
    stream = ssl.wrap_socket(sock, server_side=False, cert_reqs=ssl.CERT_REQUIRED,
                             keyfile='test/data/oa_test_client.key.pem',
                             certfile='test/data/oa_test_client.cert.pem',
                             ca_certs='test/data/chain.cert.pem')
    stream.write("GET /foo/bar\r\nAccept: application-json\r\n")

