from io import BytesIO

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine

SIZE = 40
OUT = 20
BLUE_INDEX = 1


def make_engine():
    return Engine(Context(config=Config()))


def palette_image(transparency=None):
    """40x40 palette image. Index 0 is the background, index 1 is a
    blue square in the middle. The background is opaque unless
    transparency is given, in which case it is a bytes alpha table."""
    img = Image.new("P", (SIZE, SIZE), 0)
    img.putpalette([0, 0, 0, 0, 0, 255] + [0] * 762)
    img.paste(BLUE_INDEX, (10, 10, 30, 30))
    if transparency is not None:
        img.info["transparency"] = transparency
    return img


def to_bytes(img, fmt, **kwargs):
    buffer = BytesIO()
    img.save(buffer, fmt, **kwargs)
    return buffer.getvalue()


def alpha_at(img, xy):
    return img.convert("RGBA").getpixel(xy)[3]


def resize_round_trip(source_bytes, source_ext, out_ext):
    engine = make_engine()
    engine.load(source_bytes, source_ext)
    engine.resize(OUT, OUT)
    return Image.open(BytesIO(engine.read(extension=out_ext)))


class TestGifPaletteTransparency:
    def test_transparent_palette_gif_keeps_transparent_corner(self):
        source = to_bytes(palette_image(transparency=0), "GIF", transparency=0)
        result = resize_round_trip(source, ".gif", ".gif")

        assert result.info.get("transparency") is not None
        assert alpha_at(result, (0, 0)) == 0
        assert alpha_at(result, (OUT // 2, OUT // 2)) == 255

    def test_opaque_palette_gif_stays_opaque(self):
        source = to_bytes(palette_image(), "GIF")
        result = resize_round_trip(source, ".gif", ".gif")

        assert "transparency" not in result.info
        assert alpha_at(result, (0, 0)) == 255
        assert alpha_at(result, (OUT // 2, OUT // 2)) == 255

    def test_png_output_keeps_partial_alpha_from_palette(self):
        # Background entry has alpha 128, square entry is opaque
        source = to_bytes(
            palette_image(transparency=bytes([128, 255])),
            "PNG",
            transparency=bytes([128, 255]),
        )
        engine = make_engine()
        engine.load(source, ".png")
        assert engine.original_mode == "P"
        engine.resize(OUT, OUT)
        result = Image.open(BytesIO(engine.read(extension=".png")))

        assert 0 < alpha_at(result, (0, 0)) < 255
