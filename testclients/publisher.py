import ssl
import json
from time import sleep, localtime

import paho.mqtt.client as mqtt

deployment = "../infra/configs/tmp/desktop"

with open(deployment + "/config.json") as f:
    config = json.load(f)

mqttc = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    protocol=mqtt.MQTTv5,
    client_id=config['mqtt_client_id']
)

mqttc.tls_set(
    ca_certs=deployment + "/x509/ca.pem",
    certfile=deployment + "/x509/cert.pem",
    keyfile=deployment + "/x509/key.pem",
    tls_version=ssl.PROTOCOL_TLS
)


def on_connect(client, userdata, flags, reason_code, properties):
    print("on_connect: " + str(reason_code))


def on_log(client, userdata, level, buf):
    print("log: " + buf)


mqttc.on_connect = on_connect
mqttc.on_log = on_log

mqttc.connect(host=config['mqtt_host'], port=config['mqtt_port'])

mqttc.loop_start()

while True:
    lt = localtime()
    val = ':'.join([str(lt.tm_hour), str(lt.tm_min), str(lt.tm_sec)])
    for uc in config['unicorns']:
        topic = uc['topic_base'] + '/text'
        print("publishing " + topic + ": " + val)
        print(mqttc.publish(topic, val))
    sleep(5)
