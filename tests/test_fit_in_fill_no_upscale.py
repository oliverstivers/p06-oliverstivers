# -*- coding: utf-8 -*-

# Regression test for course issue 1 (fill-no-upscale).
# fit-in + fill + no_upscale must keep the fill canvas at the requested size.

from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image
from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

COURSE_IMAGES = abspath(join(dirname(__file__), "..", "course", "images"))


class FitInFillNoUpscaleTestCase(TestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = COURSE_IMAGES
        cfg.QUALITY = "keep"

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_no_upscale_keeps_fill_canvas(self):
        response = await self.async_fetch(
            "/unsafe/fit-in/300x300/filters:fill(red):no_upscale()"
            ":format(png)/small.png"
        )
        assert response.code == 200
        size = Image.open(BytesIO(response.body)).size
        assert size == (300, 300), size
