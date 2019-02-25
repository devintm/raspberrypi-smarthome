#!/usr/bin/python
import sys
import Adafruit_DHT

while True:
    # Pin is currently GPIO24 (Pin 18)
    humidity, celsius = Adafruit_DHT.read_retry(11, 24)
    fahrenheit = (celsius * 1.8) + 32
    print 'Temp: {0:0.1f} C ({1:0.1f} F)   Humidity: {2:0.1f} %'.format(celsius, fahrenheit, humidity)

