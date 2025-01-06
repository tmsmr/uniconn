import machine
from time import sleep, sleep_ms, ticks_ms
from uclib import *


class DrawingJob:
    def __init__(self, topic, data):
        self.topic = topic
        self.data = data


class Uniconn:
    CONFIG_FILE = 'config/config.json'

    def __init__(self):
        self.wifi = None
        self.conf = None
        self.display = None
        self.mqtt = None
        self.jobs = []

    def panic(self, msg, comp):
        error(msg)
        self.display.symbol(comp, Display.RED)
        sleep(10)
        self.mqtt.disconnect()
        self.wifi.disconnect()
        machine.reset()

    def callback(self, topic, payload):
        topic = topic.decode('utf-8')
        info('received ' + str(len(payload)) + ' bytes from ' + topic)
        self.jobs.append(DrawingJob(topic, payload))

    def draw(self, job):
        start = ticks_ms()
        if job.topic.endswith('/text'):
            self.display.draw(TextFrame.from_bytes(job.data))
            info('drawing text frame took: %d ms' % (ticks_ms() - start))
        if job.topic.endswith('/pixels'):
            self.display.draw(PixelFrame.from_bytes(job.data))
            info('drawing pixels frame took: %d ms' % (ticks_ms() - start))

    def initialize(self):
        self.conf = Config.load(self.CONFIG_FILE)
        enable_logging(self.conf.logging_enabled)
        info('running with config values %s' % str(self.conf))

        self.display = Display(self.conf)
        info('display ' + str(self.display) + ' initialized')

        try:
            self.wifi = WiFi(self.conf)
            self.wifi.connect()
            info('wifi connected to ' + self.conf.wifi_ssid + ', got ip ' + self.wifi.ifconfig()[0])
            update_rtc()
            info('synchronized rtc via ntp, utc time is ' + rtc_time_str())
        except RuntimeError as e:
            self.panic(e, 'wifi')

        announcement = (
            self.conf.mqtt_status_topic,
            ujson.dumps({
                'status': 'online',
                'mqtt_topic_base': self.conf.mqtt_topic_base,
                'unicorn_type': self.conf.unicorn_type_str,
                'dimensions': {
                    'width': self.display.width,
                    'height': self.display.height
                }
            })
        )

        testament = (
            self.conf.mqtt_status_topic,
            ujson.dumps({
                'status': 'offline'
            })
        )

        try:
            self.mqtt = Mqtt(self.conf, self.callback, [
                self.conf.mqtt_topic_base + '/text',
                self.conf.mqtt_all_topic_base + '/text',
                self.conf.mqtt_topic_base + '/pixels',
                self.conf.mqtt_all_topic_base + '/pixels',
            ], announcement, testament)
            self.mqtt.connect()
            info('connected to broker ' + self.conf.mqtt_host
                 + '. subscribed to ' + ', '.join(self.mqtt.topics)
                 + '. testament set to ' + testament[0] + ': ' + testament[1])
        except Exception as e:
            self.panic(e, 'envelope')

    def run(self):
        while True:
            try:
                ping, announce = self.mqtt.tick()
                if ping:
                    info('broker ' + self.conf.mqtt_host + ' pinged')
                if announce:
                    info('announced with ' + self.mqtt.announcement[0] + ': ' + self.mqtt.announcement[1])
                if len(self.jobs) > 0:
                    self.draw(self.jobs.pop(0))
                sleep_ms(10)
            except Exception as e:
                self.panic(e, 'error')
