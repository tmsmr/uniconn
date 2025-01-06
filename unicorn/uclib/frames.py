import ujson
import binascii
import io
import deflate

class Frame:
    TEXT = 0
    PIXELS = 1

    def __init__(self, t, br, bg, bb):
        self.t = t
        self.br = br
        self.bg = bg
        self.bb = bb

    def bg_color(self):
        return self.br, self.bg, self.bb


class TextFrame(Frame):
    @staticmethod
    def from_bytes(raw):
        return TextFrame(**ujson.loads(raw))

    def __init__(self, br, bg, bb, r, g, b, v):
        Frame.__init__(self, Frame.TEXT, br, bg, bb)
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

    def __init__(self, br, bg, bb, x, y, w, h, v):
        Frame.__init__(self, Frame.PIXELS, br, bg, bb)
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
