import ssl

from umqtt.simple import MQTTClient

KEEPALIVE = 3600


def load_der(fp):
    with open(fp, 'rb') as f:
        data = f.read()
    return data


class Mqtt:
    def __init__(self, config, callback):
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        ssl_ctx.load_cert_chain(load_der('config/x509/cert.der'), load_der('config/x509/key.der'))
        ssl_ctx.load_verify_locations(cadata=load_der('config/x509/ca.der'))

        self.client = MQTTClient(
            client_id=config.client_id,
            server=config.mqtt_host,
            port=config.mqtt_port,
            keepalive=KEEPALIVE,
            ssl=ssl_ctx
        )
        self.topic = config.uniconn_topic

        self.client.set_callback(callback)

    def connect(self):
        self.client.connect()
        self.client.subscribe(self.topic)

    def poll(self):
        self.client.check_msg()
