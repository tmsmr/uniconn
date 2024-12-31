import ssl
import json

import paho.mqtt.client as mqtt
from paho.mqtt.subscribeoptions import SubscribeOptions

deployment = "../deployment/unicorns/tmp/galactic-unicorn"

with open(deployment + "/config.json") as f:
    config = json.load(f)

mqttc = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    protocol=mqtt.MQTTv5,
    client_id=config['client_id']
)

mqttc.tls_set(
    ca_certs=deployment + "/x509/ca.pem",
    certfile=deployment + "/x509/cert.pem",
    keyfile=deployment + "/x509/key.pem",
    tls_version=ssl.PROTOCOL_TLS
)


def on_connect(client, userdata, flags, reason_code, properties):
    print("on_connect: " + str(reason_code))
    print("subscribe " + config['uniconn_topic'] + ": " + client.subscribe(
        (config['uniconn_topic'], SubscribeOptions(qos=0))
    )[0].name)


def on_message(client, userdata, msg):
    print(msg.topic + ": " + msg.payload.decode())

def on_log(client, userdata, level, buf):
    print("log: " + buf)

mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_log = on_log

mqttc.connect(host=config['mqtt_host'], port=config['mqtt_port'])

mqttc.loop_forever()
