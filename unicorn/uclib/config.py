import ujson


class Config:
    class UnicornType:
        STELLAR = 0
        GALACTIC = 1
        COSMIC = 2

    @staticmethod
    def load(fp):
        with open(fp) as cf:
            data = ujson.load(cf)
        return Config(**data)

    def __init__(self, mqtt_host, mqtt_port, client_id, uniconn_topic, broadcast_topic,
                 uniconn_type, wifi_psk, wifi_ssid, wifi_country):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.client_id = client_id
        self.uniconn_topic = uniconn_topic
        self.broadcast_topic = broadcast_topic
        self.wifi_psk = wifi_psk
        self.wifi_ssid = wifi_ssid
        self.wifi_country = wifi_country

        if uniconn_type == 'STELLAR':
            self.unicorn_type = Config.UnicornType.STELLAR
        elif uniconn_type == 'GALACTIC':
            self.unicorn_type = Config.UnicornType.GALACTIC
        elif uniconn_type == 'COSMIC':
            self.unicorn_type = Config.UnicornType.COSMIC

    def __str__(self):
        return self.__dict__
