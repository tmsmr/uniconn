import ssl
from time import time
from umqtt.simple import MQTTClient

MQTT_KEEPALIVE = 300
MQTT_PING_INTERVAL = 60
MQTT_ANNOUNCE_INTERVAL = 600


def load_der(path):
    with open(path, 'rb') as f:
        data = f.read()
    return data


class Mqtt:
    def __init__(self, config, callback, topics, announcement, testament):
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        ssl_ctx.load_cert_chain(load_der('config/x509/cert.der'), load_der('config/x509/key.der'))
        ssl_ctx.load_verify_locations(cadata=load_der('config/x509/ca.der'))

        self.client = MQTTClient(
            client_id=config.mqtt_client_id,
            server=config.mqtt_host,
            port=config.mqtt_port,
            keepalive=MQTT_KEEPALIVE,
            ssl=ssl_ctx
        )
        self.topics = topics
        self.client.set_callback(callback)
        self.client.set_last_will(testament[0], testament[1])
        self.announcement = announcement
        self.last_ping = 0
        self.last_announce = 0

    def connect(self):
        try:
            self.client.connect()
        except Exception as e:
            raise RuntimeError('failed to connect to broker: ' + str(e))
        for topic in self.topics:
            try:
                self.client.subscribe(topic)
            except Exception as e:
                raise RuntimeError('failed to subscribe to topic ' + topic + ' : ' + str(e))

    def tick(self):
        try:
            self.client.check_msg()
            ping, announce = (False, False)
            now = int(time())
            if now - self.last_ping > MQTT_PING_INTERVAL:
                self.client.ping()
                self.last_ping = now
                ping = True
            if now - self.last_announce > MQTT_ANNOUNCE_INTERVAL:
                self.client.publish(self.announcement[0], self.announcement[1])
                self.last_announce = now
                announce = True
            return ping, announce
        except Exception as e:
            raise RuntimeError('lost connection to broker: ' + str(e))

    def disconnect(self):
        try:
            self.client.disconnect()
        except:
            pass
