import ntptime
from time import gmtime


def update_rtc():
    try:
        # uses pool.ntp.org
        # supports only UTC
        ntptime.settime()
    except:
        raise RuntimeError('failed to set rtc via ntp')


def rtc_time_str():
    hms = []
    for v in gmtime()[3:6]:
        hms.append('%02d' % v)
    return ':'.join(hms)
