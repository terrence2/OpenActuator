import os
import sys
sys.path.append(os.path.realpath('./OpenActuator/app_a'))
sys.path.append(os.path.realpath('./test/mock'))

if os.path.isfile('LICENSE'):
    os.chdir('./test')
import weather_stations

import json
import select
import socket


def test_weather_stations():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(('127.0.0.1', 12345))

    config = {
        "type": "DHT22",
        "id": "foo",
        "interval": [10, "ms"],
        "target": ['127.0.0.1', 12345],
        "pin": 42,
    }
    station = weather_stations.WeatherStation.from_config(config)

    station.think(1000)
    msg = server.recvfrom(1024)
    data = json.loads(msg[0])
    assert data['id'] == "foo"
    assert data['temperature'] == 42.0
    assert data['humidity'] == 0.42
    assert data['pressure'] == -1

    # interval is 10ms, so rethink after 1 should not trigger a new message.
    station.think(1001)
    ready = select.select([server], [], [], 0.5)
    assert len(ready[0]) == 0

    # interval after 10ms should send again.
    station.think(1011)
    msg = server.recvfrom(1024)
    data = json.loads(msg[0])
    assert data['id'] == "foo"
    assert data['temperature'] == 42.0
    assert data['humidity'] == 0.42
    assert data['pressure'] == -1


def test_endpoints():
    config = [{
        "type": "DHT22",
        "id": "foo",
        "interval": [10, "ms"],
        "target": ['127.0.0.1', 12345],
        "pin": 42,
    }, {
        "type": "DHT11",
        "id": "bar",
        "interval": [10, "ms"],
        "target": ['127.0.0.1', 12345],
        "pin": 43,
    }]
    stations = weather_stations.WeatherStations(config)
    resp = stations.list()
    assert resp[0] == 200
    assert len(resp[1]) > 0
    data = json.loads(resp[2])
    assert 'foo' in data
    assert 'bar' in data
    assert data['foo']['pin'] == 42
    assert data['foo']['temperature'] == 42.0
    assert data['foo']['humidity'] == 0.42

    resp = stations.show('bar')
    assert resp[0] == 200
    assert len(resp[1]) > 0
    data = json.loads(resp[2])
    assert data['pin'] == 43
    assert data['temperature'] == 42.0
    assert data['humidity'] == 0.42
