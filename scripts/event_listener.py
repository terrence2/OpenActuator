#!/usr/bin/env python3
import json
import socket


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('0.0.0.0', 33474))

    while True:
        msg = server.recvfrom(1024)
        data = json.loads(str(msg[0], 'ascii'))
        print("ID: {}, Temp: {}, Humidity: {}, Pressure: {}".format(data['id'],
                                                                    data['temperature'] * 9 / 5 + 32,
                                                                    data['humidity'],
                                                                    data['pressure']))


if __name__ == '__main__':
    main()
