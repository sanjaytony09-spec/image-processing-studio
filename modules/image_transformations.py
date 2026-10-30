"""
Image Transformations Module for Image Processing Toolkit
Handles geometric transformations (rotation, flip, crop, resize)
and photometric adjustments (brightness, contrast).
"""

import cv2
import numpy as np


def rotate_image(image: np.ndarray, angle: int) -> np.ndarray:
    """
    Rotate image by 90, 180, or 270 degrees clockwise.
    Uses dedicated cv2 rotation codes for speed and lossless transformation.
    """
    if image is None or image.size == 0:
        raise ValueError("Cannot rotate empty image.")

    norm_angle = angle % 360
    if norm_angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif norm_angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif norm_angle == 270:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif norm_angle == 0:
        return image.copy()
    else:
        # Arbitrary angle rotation around center
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        m = cv2.getRotationMatrix2D(center, -angle, 1.0)
        cos = np.abs(m[0, 0])
        sin = np.abs(m[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        m[0, 2] += (new_w / 2) - center[0]
        m[1, 2] += (new_h / 2) - center[1]
        return cv2.warpAffine(image, m, (new_w, new_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def flip_image(image: np.ndarray, direction: str = 'horizontal') -> np.ndarray:
    """
    Flip image horizontally or vertically.

    Args:
        direction: 'horizontal', 'vertical', or 'both'
    """
    if image is None or image.size == 0:
        raise ValueError("Cannot flip empty image.")

    dir_clean = direction.strip().lower()
    if dir_clean in ('horizontal', 'h'):
        return cv2.flip(image, 1)
    elif dir_clean in ('vertical', 'v'):
        return cv2.flip(image, 0)
    elif dir_clean in ('both', 'hv', 'vh'):
        return cv2.flip(image, -1)
    else:
        raise ValueError(f"Unknown flip direction '{direction}'. Use 'horizontal' or 'vertical'.")


def resize_image(image: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
    """
    Resize image to user-specified dimensions with validation.
    Chooses INTER_AREA for downsizing (avoids moire) and INTER_CUBIC for upsizing.
    """
    if image is None or image.size == 0:
        raise ValueError("Cannot resize empty image.")

    if not isinstance(target_width, (int, float)) or not isinstance(target_height, (int, float)):
        raise TypeError("Width and height must be numeric values.")

    target_w = int(round(target_width))
    target_h = int(round(target_height))

    if target_w <= 0 or target_h <= 0:
        raise ValueError(f"Resize dimensions must be positive integers (got {target_w}x{target_h}).")

    if target_w > 10000 or target_h > 10000:
        raise ValueError(f"Dimension exceeds maximum safe limit of 10000 pixels.")

    orig_h, orig_w = image.shape[:2]
    if target_w == orig_w and target_h == orig_h:
        return image.copy()

    # Interpolation choice
    if target_w < orig_w and target_h < orig_h:
        interpolation = cv2.INTER_AREA
    else:
        interpolation = cv2.INTER_CUBIC

    return cv2.resize(image, (target_w, target_h), interpolation=interpolation)


def crop_image(image: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
    """
    Crop rectangular region with boundary clamping and validation.
    Coordinates (x1, y1) to (x2, y2).
    """
    if image is None or image.size == 0:
        raise ValueError("Cannot crop empty image.")

    img_h, img_w = image.shape[:2]

    start_x = max(0, min(img_w - 1, min(int(x1), int(x2))))
    end_x = max(0, min(img_w, max(int(x1), int(x2))))
    start_y = max(0, min(img_h - 1, min(int(y1), int(y2))))
    end_y = max(0, min(img_h, max(int(y1), int(y2))))

    if (end_x - start_x) < 5 or (end_y - start_y) < 5:
        raise ValueError("Selected crop region is too small (minimum 5x5 pixels required).")

    return image[start_y:end_y, start_x:end_x].copy()


def adjust_brightness_contrast(image: np.ndarray, brightness: float = 0.0, contrast: float = 0.0) -> np.ndarray:
    """
    Adjust brightness and contrast using cv2.convertScaleAbs.

    Args:
        brightness: Shift in range [-100, 100] (0 = neutral).
        contrast: Shift in range [-100, 100] (0 = neutral).
    """
    if image is None or image.size == 0:
        raise ValueError("Cannot adjust empty image.")

    # Convert contrast slider [-100, 100] to multiplicative factor alpha
    # 0 -> 1.0 (no change), 100 -> 3.0, -100 -> 0.1
    c = max(-100.0, min(100.0, float(contrast)))
    b = max(-100.0, min(100.0, float(brightness)))

    if c >= 0:
        alpha = 1.0 + (c / 50.0)  # [1.0, 3.0]
    else:
        alpha = 1.0 + (c / 111.0)  # [0.1, 1.0]

    beta = b * 1.28  # [-128, 128]

    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return adjusted
