import base64
from io import BytesIO

from PIL import Image

from domino.testing import piece_dry_run


def _data_uri(color):
    """Build a small in-memory PNG as a data URI so the test needs no network."""
    img = Image.new("RGB", (16, 16), color)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def test_imagefilterpiece():
    input_data = dict(
        image_urls=[
            _data_uri((200, 50, 50)),
            _data_uri((50, 50, 200)),
        ],
        black_and_white=True,
        cool=True,
        output_type="both",
    )

    output = piece_dry_run(
        piece_name="ImageFilterPiece",
        input_data=input_data,
        secrets_data={},
    )

    assert len(output["out_image_paths"]) == 2
    assert len(output["out_images_base64"]) == 2
