import conf
import htserver
import machine
import net
import select
import time


def main():
    configure_cpu()
    net.connect_to_wifi()

    poller = select.poll()
    server = htserver.HttpServer(poller)

    while True:
        ready = poller.ipoll(1000)
        for tpl in ready:
            print("handling ready socket")
            server.handle_ready_socket(poller, tpl[0], tpl[1])


def configure_cpu():
    cpu_config = conf.config().get('cpu', {})
    if 'freq' in cpu_config:
        freq = int(cpu_config['freq'])
        print("Setting machine to freq: {}".format(freq))
        machine.freq(freq)


