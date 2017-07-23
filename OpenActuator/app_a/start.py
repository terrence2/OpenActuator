import conf
import htserver
import machine
import net
import select
import utime
import weather_stations


def main():
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
        ready = poller.ipoll(1000)
        for tpl in ready:
            print("handling ready socket")
            server.handle_ready_socket(*tpl)

        weather_devices.think(utime.ticks_ms())


def configure_cpu():
    cpu_config = conf.config().get('cpu', {})
    if 'freq' in cpu_config:
        freq = int(cpu_config['freq'])
        print("Setting machine to freq: {}".format(freq))
        machine.freq(freq)

