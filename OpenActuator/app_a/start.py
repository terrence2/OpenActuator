import conf
import htserver
import interrupt_vector
import machine
import net
import panic_handler
import select
import utime
import weather_stations


def _lower_half(pin, first_call_time, last_call_time):
    print("GOT LOWER HALF")


class LoopState:
    def __init__(self):
        configure_cpu()
        net.connect_to_wifi()

        iv = interrupt_vector.InterruptVector()

        button = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
        iv.register(machine.Pin.IRQ_FALLING, button, _lower_half)

        weather_devices = weather_stations.WeatherStations(conf.config().get('weather_stations', []))

        self.target_loop_time = conf.config().get("main_loop", {}).get("interval", 32)
        self.minimum_loop_time = conf.config().get("main_loop", {}).get("minimum", 1)

        self.thinkers = [
            iv,
            weather_devices
        ]

        routes = [
            ('GET', '/weather_stations/', 0, weather_devices.list),
            ('GET', '/weather_stations/(.+)', 1, weather_devices.show)
        ]

        self.poller = select.poll()
        if not hasattr(self.poller, 'ipoll'):
            import uselect
            self.poller = uselect.poll()

        self.server = htserver.HttpServer(self.poller, routes, conf.config()['http_server'])

    def loop_forever(self):
        delay = self.target_loop_time
        while True:
            before_time = utime.ticks_ms()
            self.loop_once(delay)
            delay = self.target_loop_time - (utime.ticks_ms() - before_time)
            if delay < 0:
                print("Over loop time by: {}ms".format(-delay))
                delay = self.minimum_loop_time

    def loop_once(self, target_delay):
        ready = self.poller.ipoll(target_delay)

        for tpl in ready:
            print("handling ready socket: {}".format(tpl[0]))
            self.server.handle_ready_socket(self.poller, *tpl)

        for thinker in self.thinkers:
            thinker.think(utime.ticks_ms())


def configure_cpu():
    cpu_config = conf.config().get('cpu', {})
    if 'freq' in cpu_config:
        freq = int(cpu_config['freq'])
        print("Setting machine to freq: {}".format(freq))
        machine.freq(freq)


def main():
    try:
        loop = LoopState()
        loop.loop_forever()
    except Exception as ex:
        panic_handler.send_exception_message(ex)
        utime.sleep_ms(5000)
        machine.reset()

