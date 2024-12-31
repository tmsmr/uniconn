import gc

from .wifi import Wifi
from .config import Config
from .display import Display
from .mqtt import Mqtt

def cleanup():
    gc.collect()
    log('INFO', 'gc finished')


def log(level, message):
    print('[%.fk/%.fk] %s: %s' % (gc.mem_alloc() / 1024, (gc.mem_alloc() + gc.mem_free()) / 1024, level, message))


def info(message):
    log('INFO', message)


def warn(message):
    log('WARN', message)


def error(message):
    log('ERROR', message)
