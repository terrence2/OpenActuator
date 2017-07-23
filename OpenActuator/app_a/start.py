import htserver
import net
import select


def main():
    net.connect_to_wifi()

    poller = select.poll()
    server = htserver.HttpServer(poller)

    while True:
        ready = poller.ipoll(1000)
        for tpl in ready:
            print("handling ready socket")
            server.handle_ready_socket(poller, tpl[0], tpl[1])




