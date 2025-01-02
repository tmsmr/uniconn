import ujson


class Config:
    class UnicornType:
        STELLAR = 0
        GALACTIC = 1
        COSMIC = 2

    @staticmethod
    def load(path):
        with open(path) as config_file:
            data = ujson.load(config_file)
        return Config(**data)

    def __init__(self,
                 mqtt_host, mqtt_port, mqtt_client_id, mqtt_topic_base, mqtt_all_topic_base,
                 unicorn_type,
                 wifi_psk, wifi_ssid, wifi_country):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_client_id = mqtt_client_id
        self.mqtt_topic_base = mqtt_topic_base
        self.mqtt_all_topic_base = mqtt_all_topic_base
        self.wifi_psk = wifi_psk
        self.wifi_ssid = wifi_ssid
        self.wifi_country = wifi_country

        if unicorn_type == 'STELLAR':
            self.unicorn_type = Config.UnicornType.STELLAR
        elif unicorn_type == 'GALACTIC':
            self.unicorn_type = Config.UnicornType.GALACTIC
        elif unicorn_type == 'COSMIC':
            self.unicorn_type = Config.UnicornType.COSMIC

    def __str__(self):
        return 'mqtt_host: %s, mqtt_port: %d, mqtt_client_id: %s, mqtt_topic_base: %s, mqtt_all_topic_base: %s, unicorn_type: %d, wifi_ssid: %s, wifi_country: %s' % (
            self.mqtt_host, self.mqtt_port, self.mqtt_client_id, self.mqtt_topic_base, self.mqtt_all_topic_base,
            self.unicorn_type,
            self.wifi_ssid, self.wifi_country)
