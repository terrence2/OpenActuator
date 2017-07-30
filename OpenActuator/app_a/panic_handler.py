import conf
import uio
import sys
import usocket


def send_exception_message(ex):
    capture = uio.StringIO()
    sys.print_exception(ex, capture)
    capture.seek(0)
    ex_message = capture.read()

    address = conf.config()["panic_handler"]["address"]
    port = conf.config()["panic_handler"]["port"]
    path = conf.config()["panic_handler"]["path"]

    addr_info = usocket.getaddrinfo(address, port)

    print("Sending Panic Info to:", addr_info)
    s = usocket.socket()
    s.connect(addr_info[0][-1])
    s = s.makefile("rwb", 0)
    s.write(bytes("POST {} HTTP/1.0\r\nContent-Length: {}\r\n\r\n{}".format(path, len(ex_message), ex_message), "utf-8"))
    s.read()
    s.close()
