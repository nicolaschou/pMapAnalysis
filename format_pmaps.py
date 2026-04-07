from pathlib import Path
import cv2
import numpy as np

def get_grayscale(path: Path):
    """
    Load an image from disk and return a grayscale representation while
    preserving bit depth and dynamic range.

    Uses cv2.imread() with the cv2.IMREAD_UNCHANGED flag, ensuring that:

    - The original dtype and values are preserved (e.g., uint16).
    - No normalization or rescaling is applied.
    - No color profile adjustments are performed.
    - Alpha channels are explicitly converted

    Single channel images are returned unchanged. 3-channel (BGR) or
    4-channel (BGRA) images are converted using the cv2.cvtColor() with
    the cv2.COLOR_BGR2GRAY or cv2.COLOR_BGRA2GRAY flag, respectively.
    Per the OpenCV documentation, each graylevel is calculated with:
    Y = 0.114 B + 0.587 G + 0.299 R, where the dtype of the original
    image is retained.

    https://docs.opencv.org/3.4/de/d25/imgproc_color_conversions.html#color_convert_rgb_gray

    Params:
        path (Path): Path to the image to be loaded

    Returns:
        np.ndarray: Grayscale image (H, W) with the same dtype as the input.
    """
    raw = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if raw is None:
        raise FileNotFoundError(f"Failed to load image: {path}")
    elif raw.ndim == 2:
        return raw
    elif raw.ndim == 3:
        ch = raw.shape[2]
        if ch == 3:
            print(f"{path} encoded as 3-channel image; converted to grayscale")
            return cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
        elif ch == 4:
            print(f"{path} encoded as 4-channel image; converted to grayscale")
            return cv2.cvtColor(raw, cv2.COLOR_BGRA2GRAY)
        else:
            raise ValueError(
                f"Unsupported number of channels: {ch} for image: {path}"
            )
    else:
        raise ValueError(
            f"Unsupported image shape: {raw.shape} for image: {path}"
        )
    

def apply_crop(
        img: np.ndarray,
        crop: tuple[tuple[int, int], tuple[int, int]] | None
    ):
    """Return cropped array using inclusive bounds"""
    if crop is None:
        return img
    (tl_r, tl_c), (br_r, br_c) = crop # br inclusive
    return img[tl_r:br_r+1, tl_c:br_c+1]