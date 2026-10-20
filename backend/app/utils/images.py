from dataclasses import dataclass
from io import BytesIO

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError


MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_PIXELS = 40_000_000
MIN_DIMENSION = 128
SUPPORTED_FORMATS = {"JPEG", "PNG"}


class ImageValidationError(ValueError):
    """Raised when an upload cannot safely be analyzed."""


@dataclass(frozen=True)
class ValidatedImage:
    image: Image.Image
    width: int
    height: int
    warnings: list[str]
    status: str


def validate_image(data: bytes) -> ValidatedImage:
    if not data:
        raise ImageValidationError("No image was uploaded.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ImageValidationError("The image exceeds the 10 MB upload limit.")
    try:
        with Image.open(BytesIO(data)) as source:
            source.verify()
        with Image.open(BytesIO(data)) as source:
            image = source.convert("RGB")
            width, height = image.size
            image.load()
            image_format = source.format
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageValidationError("The uploaded file is not a valid image.") from exc

    if image_format not in SUPPORTED_FORMATS:
        raise ImageValidationError("Only JPEG and PNG images are supported.")
    if width < MIN_DIMENSION or height < MIN_DIMENSION:
        raise ImageValidationError(
            f"Image dimensions must be at least {MIN_DIMENSION} by {MIN_DIMENSION} pixels."
        )
    if width * height > MAX_PIXELS:
        raise ImageValidationError("The image has too many pixels to process safely.")

    array = np.asarray(image)
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    warnings: list[str] = []
    if float(np.mean(gray)) < 35:
        warnings.append("The image may be underexposed.")
    elif float(np.mean(gray)) > 220:
        warnings.append("The image may be overexposed.")
    if float(cv2.Laplacian(gray, cv2.CV_64F).var()) < 35:
        warnings.append("The image may be blurred.")
    # A fundus detector is not assumed here; this is only a conservative quality warning.
    if min(width, height) / max(width, height) < 0.45:
        warnings.append("The image framing is unusually narrow.")

    status = "warning" if warnings else "acceptable"
    return ValidatedImage(image, width, height, warnings, status)
