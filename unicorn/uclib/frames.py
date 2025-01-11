import ujson
import binascii
import io
import deflate


class Frame:
    TEXT = 0
    PIXELS = 1
    COLOR = 2

    def __init__(self, t, d, br, bg, bb):
        self.t = t
        self.d = d
        self.br = br
        self.bg = bg
        self.bb = bb

    def __str__(self):
        if self.t == self.TEXT:
            ts = 'TEXT'
        elif self.t == self.PIXELS:
            ts = 'PIXELS'
        else:
            ts = 'COLOR'
        return '%s(%d)' % (ts, self.d)

    def temporary(self):
        return self.d > 0

    def duration(self):
        return self.d

    def bg_color(self):
        return self.br, self.bg, self.bb


class TextFrame(Frame):
    @staticmethod
    def from_bytes(raw):
        return TextFrame(**ujson.loads(raw))

    def __init__(self, d, br, bg, bb, r, g, b, v):
        Frame.__init__(self, Frame.TEXT, d, br, bg, bb)
        self.r = r
        self.g = g
        self.b = b
        self.v = v

    def text_color(self):
        return self.r, self.g, self.b

    def text(self):
        return self.v


class PixelFrame(Frame):
    @staticmethod
    def from_bytes(raw):
        return PixelFrame(**ujson.loads(raw))

    def __init__(self, d, br, bg, bb, x, y, w, h, v):
        Frame.__init__(self, Frame.PIXELS, d, br, bg, bb)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.v = v

    def colormap(self):
        b64 = self.v.encode('utf-8')
        zipped = binascii.a2b_base64(b64)
        data = deflate.DeflateIO(io.BytesIO(zipped), deflate.GZIP, 15).read()
        return data


class ColorFrame(Frame):
    @staticmethod
    def from_bytes(raw):
        return ColorFrame(**ujson.loads(raw))

    def __init__(self, d, br, bg, bb):
        Frame.__init__(self, Frame.COLOR, d, br, bg, bb)
