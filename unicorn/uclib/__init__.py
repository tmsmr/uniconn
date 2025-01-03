import gc

from .wifi import WiFi, disable
from .config import Config
from .display import Display
from .mqtt import Mqtt


def run_gc():
    before = gc.mem_alloc()
    gc.collect()
    log('INFO', 'gc freed %.fk' % ((before - gc.mem_alloc()) / 1024))


def log(level, message):
    print('[%.fk/%.fk] %s: %s' % (gc.mem_alloc() / 1024, (gc.mem_alloc() + gc.mem_free()) / 1024, level, message))


def info(message):
    log('INFO', message)


def warn(message):
    log('WARN', message)


def error(message):
    log('ERROR', message)
