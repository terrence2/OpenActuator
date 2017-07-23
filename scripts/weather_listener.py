#!/usr/bin/env python3
import socket


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('0.0.0.0', 33474))

    while True:
        msg = server.recvfrom(1024)
        data = json.loads(msg[0])
        print("Temp: {}, Humidity: {}, Pressure: {}".format(data['temperature'], data['humidity'], data['pressure']))


if __name__ == '__main__':
    main()
