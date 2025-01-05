import network
from time import sleep_ms


class WiFi:
    CYW43_NONE_PM = 0xA11140
    CYW43_DEFAULT_PM = 0xA11142

    CYW43_LINK_STATUS = {
        -3: 'CYW43_LINK_BADAUTH',
        -2: 'CYW43_LINK_NONET',
        -1: 'CYW43_LINK_FAIL',
        0: 'CYW43_LINK_DOWN',
        1: 'CYW43_LINK_JOIN',
        2: 'CYW43_LINK_NOIP',
        3: 'CYW43_LINK_UP'
    }

    def __init__(self, config):
        self.ssid = config.wifi_ssid
        self.psk = config.wifi_psk
        network.country(config.wifi_country)
        self.nic = network.WLAN(network.STA_IF)

    def connect(self, timeout=30, pm=True):
        self.nic.active(True)
        if pm:
            self.nic.config(pm=self.CYW43_DEFAULT_PM)
        else:
            self.nic.config(pm=self.CYW43_NONE_PM)
        self.nic.connect(self.ssid, self.psk)
        status = 0
        for _ in range(timeout * 10):
            status = self.nic.status()
            # status < 0: connection failed
            # status >= 3: link up
            if status < 0 or status >= 3:
                break
            sleep_ms(100)
        if status != 3:
            raise RuntimeError('wifi connection failed with status: %d (%s)' % (status, self.CYW43_LINK_STATUS[status]))

    def ifconfig(self):
        return self.nic.ifconfig()

    def connected(self):
        return self.nic.isconnected()

    def disconnect(self):
        try:
            self.nic.disconnect()
            self.nic.active(False)
            self.nic.deinit()
        except:
            pass
