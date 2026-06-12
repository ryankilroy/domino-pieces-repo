import base64
import os
from io import BytesIO
from pathlib import Path

import numpy as np
import requests
from PIL import Image

from domino.base_piece import BasePiece

from .models import InputModel, OutputModel


# Hardcode input image URLs here to override whatever is passed in `input_data.image_urls`.
# Leave the list empty to use the URLs supplied through the piece input instead.
HARDCODED_IMAGE_URLS = [
    # "https://example.com/image1.jpg",
    # "https://example.com/image2.png",
]


filter_masks = {
    'sepia': ((0.393, 0.769, 0.189), (0.349, 0.686, 0.168), (0.272, 0.534, 0.131)),
    'black_and_white': ((0.333, 0.333, 0.333), (0.333, 0.333, 0.333), (0.333, 0.333, 0.333)),
    'brightness': ((1.4, 0, 0), (0, 1.4, 0), (0, 0, 1.4)),
    'darkness': ((0.6, 0, 0), (0, 0.6, 0), (0, 0, 0.6)),
    'contrast': ((1.2, 0.6, 0.6), (0.6, 1.2, 0.6), (0.6, 0.6, 1.2)),
    'red': ((1.6, 0, 0), (0, 1, 0), (0, 0, 1)),
    'green': ((1, 0, 0), (0, 1.6, 0), (0, 0, 1)),
    'blue': ((1, 0, 0), (0, 1, 0), (0, 0, 1.6)),
    'cool': ((0.9, 0, 0), (0, 1.1, 0), (0, 0, 1.3)),
    'warm': ((1.2, 0, 0), (0, 0.9, 0), (0, 0, 0.8)),
}


class ImageFilterPiece(BasePiece):

    def piece_function(self, input_data: InputModel):

        # Build the list of filters to apply (same for every image)
        flags = [
            'sepia', 'black_and_white', 'brightness', 'darkness', 'contrast',
            'red', 'green', 'blue', 'cool', 'warm',
        ]
        all_filters = [name for name in flags if getattr(input_data, name)]
        self.logger.info(f"Applying filters: {', '.join(all_filters)}")

        # Use hardcoded URLs if provided, otherwise fall back to the piece input
        image_urls = HARDCODED_IMAGE_URLS or input_data.image_urls

        out_image_paths = []
        out_images_base64 = []
        display_items = []

        for index, image_url in enumerate(image_urls):
            image = self._load_image(image_url)

            # Convert Image to NumPy array
            np_image = np.array(image, dtype=float)

            # Apply filters
            for filter_name in all_filters:
                np_mask = np.array(filter_masks[filter_name], dtype=float)
                np_image[..., :3] = np_image[..., :3] @ np_mask.T
                np_image = np.clip(np_image, 0, 255)

            # Convert back to uint8 and PIL image
            modified_image = Image.fromarray(np_image.astype(np.uint8))

            # Save to file
            image_file_path = ""
            if input_data.output_type in ("file", "both"):
                image_file_path = os.path.join(self.results_path, f"modified_image_{index}.png")
                modified_image.save(image_file_path, format="PNG")
                out_image_paths.append(image_file_path)

            # Convert to base64 string
            image_base64_string = ""
            if input_data.output_type in ("base64_string", "both"):
                buffered = BytesIO()
                modified_image.save(buffered, format="PNG")
                image_base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
                out_images_base64.append(image_base64_string)

            display_items.append({
                "file_type": "png",
                "base64_content": image_base64_string,
                "file_path": image_file_path,
            })

        self.display_result = display_items

        return OutputModel(
            out_image_paths=out_image_paths,
            out_images_base64=out_images_base64,
        )

    def _load_image(self, image_url: str) -> Image.Image:
        """Load a single image from an http(s) URL, a local file path, or a base64/data-URI string."""
        source = image_url.strip()

        # Remote URL
        if source.startswith(("http://", "https://")):
            self.logger.info(f"Downloading image from {source}")
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            return Image.open(BytesIO(response.content)).convert("RGB")

        # data: URI -> keep only the base64 payload
        if source.startswith("data:"):
            source = source.split(",", 1)[1]

        # Local file path
        max_path_size = int(os.pathconf('/', 'PC_PATH_MAX'))
        if len(source) < max_path_size and Path(source).is_file():
            return Image.open(source).convert("RGB")

        # Fall back to treating the string as raw base64-encoded image bytes
        self.logger.info("Input is not a URL or file path, trying to decode as base64 string")
        try:
            return Image.open(BytesIO(base64.b64decode(source))).convert("RGB")
        except Exception:
            raise ValueError("Input image is not a URL, file path, or base64 encoded string")
