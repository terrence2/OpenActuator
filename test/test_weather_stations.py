import os
import sys
sys.path.append(os.path.realpath('./OpenActuator/app_a'))
sys.path.append(os.path.realpath('./test/mock'))

os.chdir('./test')
import weather_stations

import json
import socket


def test_weather_stations():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('127.0.0.1', 12345))

    config = {
        "type": "DHT22",
        "interval": [10, "ms"],
        "target": ['127.0.0.1', 12345],
        "pin": 42,
    }
    station = weather_stations.WeatherStation.from_config(config)
    station.think(1000)

    msg = server.recvfrom(1024)
    data = json.loads(msg[0])
    assert data['temperature'] == 42.0
    assert data['humidity'] == 0.42
    assert data['pressure'] == -1

