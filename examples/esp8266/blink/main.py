# main.py -- put your code here!
from machine import Pin, Timer

led = Pin(2, Pin.OUT)

timer = Timer(-1)
timer.init(mode=Timer.PERIODIC, period=1000,
            callback=lambda _: led.value(not led.value()))