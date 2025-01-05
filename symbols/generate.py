import glob

from PIL import Image

symbols = {}

for f in glob.glob('./*.png'):
    png = Image.open(f)
    pixels = []
    for x in range(png.width):
        for y in range(png.height):
            p = png.getpixel((x, y))
            if (p[0]+p[1]+p[2])/3 < 128:
                pixels.append((x, y))
    symbols[f] = pixels
    print(f, pixels)
