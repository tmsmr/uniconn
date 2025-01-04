import machine
import ujson
from time import sleep
from uclib import *


class DrawingJob:
    class DrawingType:
        TEXT = 0

    def __init__(self, dtype, data):
        self.dtype = dtype
        self.data = data


class Uniconn:
    CONFIG_FILE = 'config/config.json'

    def __init__(self):
        self.conf = None
        self.display = None
        self.mqtt = None
        self.jobs = []

    def panic(self, msg, comp):
        self.display.write(comp, error=True)
        error(msg)
        sleep(10)
        machine.reset()

    def callback(self, topic, payload):
        topic = topic.decode('utf-8')
        info('received ' + str(len(payload)) + ' bytes from ' + topic)
        if topic.endswith('/text'):
            self.jobs.append(DrawingJob(DrawingJob.DrawingType.TEXT, payload))

    def draw(self, job):
        if job.dtype == DrawingJob.DrawingType.TEXT:
            payload = job.data.decode('utf-8')
            info('writing "' + payload + '" to display')
            self.display.write(payload)

    def initialize(self):
        self.conf = Config.load(self.CONFIG_FILE)
        enable_logging(self.conf.logging_enabled)
        info('running with config values %s' % str(self.conf))

        self.display = Display(self.conf)
        info('display ' + str(display) + ' initialized')

        try:
            w = WiFi(self.conf)
            w.connect()
            info('wifi connected to ' + self.conf.wifi_ssid + ', got ip ' + w.ifconfig()[0])
            update_rtc()
            info('synchronized rtc via ntp, utc time is ' + rtc_time_str())
        except RuntimeError as e:
            self.panic(e, 'WIFI')

        self.display.write('WIFI', success=True)
        sleep(1)
        self.display.clear()

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
                self.conf.mqtt_topic_base + '/pixels',
                ], announcement, testament)
            self.mqtt.connect()
            info('connected to broker ' + self.conf.mqtt_host
                 + '. subscribed to ' + ', '.join(self.mqtt.topics)
                 + '. testament set to ' + testament[0] + ': ' + testament[1])
        except Exception as e:
            self.panic(e, 'MQTT')

        self.display.write('MQTT', success=True)
        sleep(1)
        self.display.clear()

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
            except Exception as e:
                self.panic(e, 'MQTT')
