from PIL import Image
from tornado.testing import gen_test

from tests.base import TestCase
from tests.fixtures.transformer_test_data import TestData
from thumbor.engines.pil import Engine
from thumbor.transformer import Transformer

# (source_w, source_h, target_w, target_h, fit_in, exp_w, exp_h)
EXTREME_CASES = [
    (16, 16, 800, 20, False, 800, 20),
    (16, 16, 20, 800, False, 20, 800),
    (940, 2, 1, 1, True, 1, 1),
    (2, 940, 1, 1, True, 1, 1),
    (940, 2, 100, 0, True, 100, 1),
    (2, 940, 0, 100, True, 1, 100),
]


class ExtremeAspectResizeTestCase(TestCase):
    @gen_test
    async def test_extreme_aspect_resize_keeps_one_pixel_minimum(self):
        for case in EXTREME_CASES:
            source_w, source_h, target_w, target_h = case[:4]
            fit_in, exp_w, exp_h = case[4:]
            data = TestData(
                source_width=source_w,
                source_height=source_h,
                target_width=target_w,
                target_height=target_h,
                halign="center",
                valign="middle",
                focal_points=[],
                crop_left=0,
                crop_top=0,
                crop_right=0,
                crop_bottom=0,
                fit_in=fit_in,
            )
            context = data.to_context()
            engine = Engine(context)
            engine.image = Image.new(
                "RGBA",
                (source_w, source_h),
                (200, 100, 50, 255),
            )
            context.modules.engine = engine
            context.request.engine = engine
            engine.extension = ".png"
            trans = Transformer(context)

            await trans.transform()

            label = (
                f"{source_w}x{source_h} -> {target_w}x{target_h} "
                f"fit_in={fit_in}"
            )
            assert engine.size == (exp_w, exp_h), label
            alpha_max = engine.image.getchannel("A").getextrema()[1]
            assert alpha_max > 0, label
