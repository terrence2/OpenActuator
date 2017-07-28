import conf
import htserver
import interrupt_vector
import machine
import net
import select
import utime
import weather_stations


def _lower_half(pin, first_call_time, last_call_time):
    print("GOT LOWER HALF")


def main():
    iv = interrupt_vector.InterruptVector()

    button = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
    iv.register(machine.Pin.IRQ_FALLING, button, _lower_half)

    configure_cpu()
    net.connect_to_wifi()

    weather_devices = weather_stations.WeatherStations(conf.config().get('weather_stations', []))

    routes = [
        ('GET', '/weather_stations/', 0, weather_devices.list),
        ('GET', '/weather_stations/(.+)', 1, weather_devices.show)
    ]

    poller = select.poll()
    server = htserver.HttpServer(poller, routes, conf.config()['http_server'])

    while True:
        print("a")
        ready = poller.ipoll(5000)
        print("b")

        iv.think()

        for tpl in ready:
            print("handling ready socket: {}, {}".format(tpl[0], pipe))
            server.handle_ready_socket(*tpl)

            if tpl[0] == pipe:
                pipe.seek(0)
                print("GOT BOTTOM HALF")

        iv.think()

        weather_devices.think(utime.ticks_ms())


def configure_cpu():
    cpu_config = conf.config().get('cpu', {})
    if 'freq' in cpu_config:
        freq = int(cpu_config['freq'])
        print("Setting machine to freq: {}".format(freq))
        machine.freq(freq)

