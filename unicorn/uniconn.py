import machine
from time import sleep, sleep_ms, ticks_ms
from uclib import *


class Uniconn:
    CONFIG_FILE = 'config/config.json'

    def __init__(self):
        self.wifi = None
        self.conf = None
        self.display = None
        self.mqtt = None
        self.tick_ms = 10

        self.permanent = ColorFrame(0, 0, 0, 0)
        self.remaining = 0.0

    def panic(self, msg, comp):
        error(msg)
        self.display.symbol(comp, Display.RED)
        sleep(10)
        self.mqtt.disconnect()
        self.wifi.disconnect()
        machine.reset()

    def callback(self, topic, payload):
        run_gc()

        topic = topic.decode('utf-8')
        info('received ' + str(len(payload)) + ' bytes from ' + topic)

        if topic.endswith('/text'):
            frame = TextFrame.from_bytes(payload)
        elif topic.endswith('/pixels'):
            frame = PixelFrame.from_bytes(payload)
        else:
            frame = ColorFrame(0, 0, 0, 0)

        self.draw(frame)

        if frame.temporary():
            self.remaining = float(frame.duration()) * 1000
        else:
            self.permanent = frame

    def draw(self, frame):
        start = ticks_ms()
        self.display.draw(frame)
        info('drawing frame %s took: %d ms' % (frame, ticks_ms() - start))

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

        self.draw(self.permanent)

    def run(self):
        while True:
            try:
                ping, announce = self.mqtt.tick()
                if ping:
                    info('broker ' + self.conf.mqtt_host + ' pinged')
                if announce:
                    info('announced with ' + self.mqtt.announcement[0] + ': ' + self.mqtt.announcement[1])

                if self.remaining > 0:
                    self.remaining -= self.tick_ms
                    if self.remaining <= 0:
                        self.draw(self.permanent)

                sleep_ms(self.tick_ms)
            except Exception as e:
                self.panic(e, 'error')
