from network import WLAN, STA_IF
import rp2
import ntptime
from time import sleep_ms


class Wifi:
    def __init__(self, config):
        self.ssid = config.wifi_ssid
        self.psk = config.wifi_psk
        rp2.country(config.wifi_country)
        self.iface = WLAN(STA_IF)

    def connect(self, timeout=10):
        self.iface.active(True)
        self.iface.connect(self.ssid, self.psk)
        for _ in range(timeout * 10):
            if not 0 <= self.iface.status() <= 3:
                break
            sleep_ms(100)
        res = self.iface.status()
        if res != 3:
            raise RuntimeError('wifi connection failed with status %d' % res)
        try:
            ntptime.settime()
        except Exception:
            raise RuntimeError('failed to get/set time via NTP')
        return self.iface.ifconfig()[0]
