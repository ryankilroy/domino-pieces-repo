from domino.testing import piece_dry_run

# Precomputed tiny 2x2 PNGs as base64 data URIs. Kept as constants so this test
# module imports with no image libraries on the CI runner host — Pillow/numpy
# only need to exist inside the piece's built image, where the piece actually runs.
_RED_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAEklEQVR4nGO8o6HBwMDAxAAGAA7uATD++YiCAAAAAElFTkSuQmCC"
_BLUE_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAEklEQVR4nGPU0LjDwMDAxAAGAA2GATBumJCjAAAAAElFTkSuQmCC"


def test_imagefilterpiece():
    input_data = dict(
        image_urls=[
            f"data:image/png;base64,{_RED_PNG}",
            f"data:image/png;base64,{_BLUE_PNG}",
        ],
        black_and_white=True,
        cool=True,
        output_type="both",
    )

    output = piece_dry_run(
        piece_name="ImageFilterPiece",
        input_data=input_data,
    )

    assert len(output["out_image_paths"]) == 2
    assert len(output["out_images_base64"]) == 2
