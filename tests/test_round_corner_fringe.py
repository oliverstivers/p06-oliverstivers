import pytest

from thumbor.ext.filters import _round_corner

WIDTH = 20
HEIGHT = 20
CANVAS_RGB = (200, 100, 50)


def _apply(a_radius, b_radius, alpha):
    data = bytes([*CANVAS_RGB, alpha] * WIDTH * HEIGHT)
    out = _round_corner.apply(
        1,
        "RGBA",
        a_radius,
        b_radius,
        0,
        0,
        0,
        WIDTH,
        HEIGHT,
        data,
        1,
    )
    return [tuple(out[i : i + 4]) for i in range(0, len(out), 4)]


@pytest.mark.parametrize("a_radius,b_radius", [(6, 6), (8, 4), (4, 8)])
@pytest.mark.parametrize("alpha", [255, 128])
def test_transparent_round_corner_edge_keeps_color_and_fades_alpha(
    a_radius, b_radius, alpha
):
    pixels = _apply(a_radius, b_radius, alpha)

    # Pre-existing alpha is never raised.
    assert all(p[3] <= alpha for p in pixels)

    # Every pixel that is still visible keeps the canvas RGB, edge included.
    visible = [p for p in pixels if p[3] > 0]
    assert visible, "expected visible pixels"
    for r, g, b, _ in visible:
        assert (r, g, b) == CANVAS_RGB, "pixel colour was changed"

    # The curve is smoothed through alpha: partial-alpha edge pixels exist.
    edge = [p for p in pixels if 0 < p[3] < alpha]
    assert edge, "expected partially transparent edge pixels"
