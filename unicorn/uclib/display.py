from picographics import PicoGraphics


class Display:
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

    def success(self):
        self.graphics.set_pen(self.graphics.create_pen(0, 40, 0))
        self.graphics.clear()
        self.unicorn.update(self.graphics)

    def error(self):
        self.graphics.set_pen(self.graphics.create_pen(40, 0, 0))
        self.graphics.clear()
        self.unicorn.update(self.graphics)

    def clear(self):
        self.graphics.set_pen(self.graphics.create_pen(0, 0, 0))
        self.graphics.clear()
        self.unicorn.update(self.graphics)

    def write(self, message):
        self.graphics.set_pen(self.graphics.create_pen(0, 0, 0))
        self.graphics.clear()
        self.graphics.set_font("bitmap8")
        width = self.graphics.measure_text(message, scale=1)
        if width > self.width:
            self.error()
            return
        x = round((self.width - width) / 2)
        y = round((self.height - 8) / 2)
        self.graphics.set_pen(self.graphics.create_pen(40, 40, 40))
        self.graphics.text(message, x, y, scale=1)
        self.unicorn.update(self.graphics)
