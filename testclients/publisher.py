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

def on_message(client, userdata, msg):
    print(msg.topic + ": " + msg.payload.decode())

mqttc.on_connect = on_connect
mqttc.on_log = on_log
mqttc.on_message = on_message

mqttc.connect(host=config['mqtt_host'], port=config['mqtt_port'])

mqttc.subscribe(config['mqtt_status_topic_base'] + '/+')

mqttc.loop_start()

while True:
    lt = localtime()
    val = ':'.join([str(lt.tm_hour), str(lt.tm_min)])
    all_topic = config['mqtt_all_topic_base'] + '/text'
    print("publishing " + all_topic + ": " + val)
    print(mqttc.publish(all_topic, val))
    for uc in config['unicorns']:
        topic = uc['mqtt_topic_base'] + '/text'
        print("publishing " + topic + ": " + val)
        print(mqttc.publish(topic, val))
    sleep(60)
