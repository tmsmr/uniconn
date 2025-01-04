import ssl
import json
from time import sleep, localtime

import paho.mqtt.client as mqtt

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

while True:
    lt = localtime()
    val = ':'.join(['%02d' % lt.tm_hour, '%02d' % lt.tm_min])
    for uc in config['unicorns']:
        topic = uc['mqtt_topic_base'] + '/text'
        mqttc.publish(topic, val)
    sleep(60)
