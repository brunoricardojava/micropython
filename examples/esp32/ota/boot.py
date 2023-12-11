# boot.py -- run on boot-up
import network
from secret import ssid, password


sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

sta_if.connect(ssid, password)

print("Connecting...")
while not sta_if.isconnected():
    print(".", end='')

print("...Connected")

print(f"Network config: {sta_if.ifconfig()}")