import machine

from time import sleep, sleep_ms

from uclib import *

def fatal(e, comp):
    display.write(comp, error=True)
    error(e)
    sleep(60)
    machine.reset()

c = Config.load('config/config.json')
info(str(c))

display = Display(c)
info(str(display) + ' initialized')

try:
    ip = Wifi(c).connect()
except RuntimeError as e:
    fatal(e, 'WIFI')
info('wifi connected to ' + c.wifi_ssid + ', got IP ' + ip)
display.write('WIFI', success=True)
sleep(2)
display.clear()

def on_message(topic, payload):
    info(topic + ':' + payload)
    display.write(payload)
    cleanup()
try:
    m = Mqtt(c, on_message)
    m.connect()
except Exception as e:
    fatal(e, 'MQTT')
info('connected to broker ' + c.mqtt_host + ', subscribed to ' + c.uniconn_topic)
display.write('MQTT', success=True)
sleep(2)
display.clear()

cleanup()

while True:
    m.poll()
    sleep_ms(100)
