# boot.py -- run on boot-up
import network
from time import sleep_ms
from secret import ssid, password


station = network.WLAN(network.STA_IF)
station.active(True)

station.connect(ssid, password)

print("Connecting", end="")

while not station.isconnected():
    print(".", end="")
    sleep_ms(500)

print(f"Conected. Network config: {station.ifconfig()}")
