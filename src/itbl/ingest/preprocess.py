"""Image preprocessing: rotate, deskew, denoise, binarize."""

import numpy as np
from PIL import Image

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def preprocess_image(
    image: Image.Image,
    dpi: int = 300,
    auto_rotate: bool = True,
    deskew: bool = True,
    denoise: bool = True,
    binarize: bool = False,
) -> Image.Image:
    """
    Preprocess image for OCR.
    
    Args:
        image: PIL Image
        dpi: Target DPI (affects scaling)
        auto_rotate: Auto-detect and fix rotation
        deskew: Correct skew
        denoise: Apply denoising
        binarize: Convert to binary (black/white)
    
    Returns:
        Preprocessed PIL Image
    """
    if not CV2_AVAILABLE:
        # Fallback: minimal preprocessing with PIL only
        return image

    # Convert PIL to OpenCV format
    img_array = np.array(image.convert("RGB"))
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # Auto-rotate based on EXIF
    if auto_rotate:
        img_cv = _apply_exif_rotation(image, img_cv)

    # Convert to grayscale
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_cv

    # Denoise
    if denoise:
        gray = cv2.fastNlMeansDenoising(gray, None, h=10)

    # Deskew
    if deskew:
        gray = _deskew_image(gray)

    # Binarize (threshold)
    if binarize:
        _, gray = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

    # Convert back to PIL
    if len(image.mode) == "RGB" or not binarize:
        result = Image.fromarray(gray).convert("RGB")
    else:
        result = Image.fromarray(gray).convert("L")

    return result


def _apply_exif_rotation(pil_image: Image.Image, cv_image: np.ndarray) -> np.ndarray:
    """Apply EXIF orientation to OpenCV image."""
    try:
        exif = pil_image._getexif()
        if exif is None:
            return cv_image

        orientation = exif.get(274)  # EXIF orientation tag
        if orientation == 3:
            cv_image = cv2.rotate(cv_image, cv2.ROTATE_180)
        elif orientation == 6:
            cv_image = cv2.rotate(cv_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif orientation == 8:
            cv_image = cv2.rotate(cv_image, cv2.ROTATE_90_CLOCKWISE)
    except Exception:
        pass  # No EXIF or error reading
    return cv_image


def _deskew_image(gray: np.ndarray) -> np.ndarray:
    """Detect and correct skew in image."""
    if not CV2_AVAILABLE:
        return gray

    # Create binary image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours and compute angle
    coords = np.column_stack(np.where(binary > 0))
    if len(coords) < 10:
        return gray  # Not enough content to deskew

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Only correct if angle is significant
    if abs(angle) < 0.5:
        return gray

    # Rotate image
    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )

    return rotated

