from picographics import PicoGraphics

from .symbols import SYMBOLS
from .frames import *


class Display:
    class Color:
        def __init__(self, r, g, b):
            self.r = r
            self.g = g
            self.b = b

        def rgb(self):
            return self.r, self.g, self.b

    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)
    RED = Color(255, 0, 0)

    def __init__(self, config):
        if config.unicorn_type is config.UnicornType.STELLAR:
            from stellar import StellarUnicorn as Unicorn
            from picographics import DISPLAY_STELLAR_UNICORN as DISPLAY
        elif config.unicorn_type is config.UnicornType.GALACTIC:
            from galactic import GalacticUnicorn as Unicorn
            from picographics import DISPLAY_GALACTIC_UNICORN as DISPLAY
        elif config.unicorn_type is config.UnicornType.COSMIC:
            from cosmic import CosmicUnicorn as Unicorn
            from picographics import DISPLAY_COSMIC_UNICORN as DISPLAY
        else:
            raise RuntimeError('invalid unicorn_type')
        self.unicorn = Unicorn()
        self.graphics = PicoGraphics(DISPLAY)
        self.width = self.unicorn.WIDTH
        self.height = self.unicorn.HEIGHT
        self.unicorn.set_brightness(1.0)

    def __str__(self):
        return '%s (%dx%d)' % (type(self.unicorn).__name__, self.width, self.height)

    def update(self):
        self.unicorn.update(self.graphics)

    def clear(self):
        self.graphics.set_pen(self.graphics.create_pen(*Display.BLACK.rgb()))
        self.graphics.clear()
        self.update()

    def symbol(self, name, color=None):
        self.clear()
        xd = round((self.width / 2) - (9 / 2))
        yd = round((self.height / 2) - (9 / 2))
        self.graphics.set_pen(self.graphics.create_pen(*color.rgb()))
        for p in SYMBOLS[name]:
            self.graphics.pixel(xd + p[0], yd + p[1])
        self.update()

    def draw(self, frame):
        if frame.t == Frame.TEXT:
            self.graphics.set_pen(self.graphics.create_pen(*frame.bg_color()))
            self.graphics.clear()
            self.graphics.set_font("bitmap8")
            message = frame.text()
            width = self.graphics.measure_text(message, scale=1)
            if width > self.width:
                message = '...'
                width = self.graphics.measure_text(message, scale=1)
            x = round((self.width - width) / 2)
            y = round((self.height - 8) / 2)
            self.graphics.set_pen(self.graphics.create_pen(*frame.text_color()))
            self.graphics.text(message, x, y, scale=1)
            self.update()
        if frame.t == Frame.PIXELS:
            if frame.w < self.width or frame.h < self.height:
                self.graphics.set_pen(self.graphics.create_pen(*frame.bg_color()))
                self.graphics.clear()
            colormap = frame.colormap()
            for y in range(frame.h):
                for x in range(frame.w):
                    lookup = (y * frame.w) * 3
                    self.graphics.set_pen(self.graphics.create_pen(*colormap[lookup:lookup + 3]))
                    self.graphics.pixel(frame.x + x, frame.y + y)
            self.update()
