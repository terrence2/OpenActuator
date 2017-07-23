import conf
import htserver
import machine
import net
import select
import utime


def main():
    configure_cpu()
    net.connect_to_wifi()

    weather_stations = configure_weather_stations()

    poller = select.poll()
    server = htserver.HttpServer(poller)

    while True:
        ready = poller.ipoll(1000)
        for tpl in ready:
            print("handling ready socket")
            server.handle_ready_socket(poller, tpl[0], tpl[1])

        for station in weather_stations:
            station.think(utime.ticks_ms())


def configure_cpu():
    cpu_config = conf.config().get('cpu', {})
    if 'freq' in cpu_config:
        freq = int(cpu_config['freq'])
        print("Setting machine to freq: {}".format(freq))
        machine.freq(freq)


def configure_weather_stations():
    import weather_stations
    stations = []
    for station_config in conf.config().get('weather_stations', []):
        station = weather_stations.WeatherStation.from_config(station_config)
        stations.append(station)
    return stations
