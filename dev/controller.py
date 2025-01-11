import binascii
import ssl
import json
import gzip
from time import sleep, localtime

import paho.mqtt.client as mqtt

from random import randrange

deployment = '../infra/configs/tmp/desktop'

with open(deployment + '/config.json') as f:
    config = json.load(f)

mqttc = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    protocol=mqtt.MQTTv5,
    client_id=config['mqtt_client_id']
)

mqttc.tls_set(
    ca_certs=deployment + '/x509/ca.pem',
    certfile=deployment + '/x509/cert.pem',
    keyfile=deployment + '/x509/key.pem',
    tls_version=ssl.PROTOCOL_TLS
)


def on_connect(client, userdata, flags, reason_code, properties):
    print(reason_code)


def on_log(client, userdata, level, buf):
    print(buf)


mqttc.on_connect = on_connect
mqttc.on_log = on_log

mqttc.connect(host=config['mqtt_host'], port=config['mqtt_port'])

mqttc.loop_start()

sleep(1)

frames = ['text', 'big', 'small']

while True:
    for frame in frames:
        if frame == 'text':
            lt = localtime()
            val = ':'.join(['%02d' % lt.tm_hour, '%02d' % lt.tm_min])
            payload = {
                'd': 0,
                'br': 0,
                'bg': 0,
                'bb': 0,
                'r': 255,
                'g': 255,
                'b': 255,
                'v': val
            }
            topic = config['mqtt_all_topic_base'] + '/text'
            mqttc.publish(topic, json.dumps(payload))
        else:
            data = bytearray(b'')
            for y in range(11):
                for x in range(53):
                    if frame == 'big':
                        p = (randrange(256), randrange(256), randrange(256))
                    else:
                        rgb = 255 if x % 2 == 0 else 0
                        p = (rgb, rgb, rgb)
                    pb = bytearray(p)
                    data.extend(pb)
            zipped = gzip.compress(data)
            b64 = binascii.b2a_base64(zipped)
            val = b64.decode('utf-8')
            payload = {
                'd': 1,
                'br': 0,
                'bg': 0,
                'bb': 0,
                'x': 0,
                'y': 0,
                'w': 53,
                'h': 11,
                'v': val
            }
            topic = config['mqtt_all_topic_base'] + '/pixels'
            mqttc.publish(topic, json.dumps(payload))
        sleep(10)
