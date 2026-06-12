from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class OutputTypeType(str, Enum):
    """Output type for the result images"""
    file = "file"
    base64_string = "base64_string"
    both = "both"


class InputModel(BaseModel):
    """ImageFilterPiece Input"""
    image_urls: List[str] = Field(
        default=[],
        description="List of images to filter. Each item may be an http(s) URL, a local file path, or a base64/data-URI string. Add one entry per image in the UI.",
        json_schema_extra={"from_upstream": "allowed"},
    )
    sepia: bool = Field(default=False, description="Apply sepia effect.")
    black_and_white: bool = Field(default=False, description="Apply black and white effect.")
    brightness: bool = Field(default=False, description="Apply brightness effect.")
    darkness: bool = Field(default=False, description="Apply darkness effect.")
    contrast: bool = Field(default=False, description="Apply contrast effect.")
    red: bool = Field(default=False, description="Apply red effect.")
    green: bool = Field(default=False, description="Apply green effect.")
    blue: bool = Field(default=False, description="Apply blue effect.")
    cool: bool = Field(default=False, description="Apply cool effect.")
    warm: bool = Field(default=False, description="Apply warm effect.")
    output_type: OutputTypeType = Field(
        default=OutputTypeType.both,
        description="Format of the output images. Options are: `file`, `base64_string`, `both`.",
    )


class OutputModel(BaseModel):
    """ImageFilterPiece Output"""
    out_image_paths: List[str] = Field(
        default=[],
        description="Paths to the filtered image files (one per input image).",
    )
    out_images_base64: List[str] = Field(
        default=[],
        description="Base64-encoded strings of the filtered images (one per input image).",
    )


class SecretsModel(BaseModel):
    """ImageFilterPiece Secrets"""
