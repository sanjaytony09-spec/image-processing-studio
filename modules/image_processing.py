"""
Image Processing Filters Module for Image Processing Toolkit
Provides OpenCV-based image filters, noise reduction, sharpening,
edge detection, artistic effects, and contrast enhancement.
"""

import cv2
import numpy as np


def ensure_bgr(image: np.ndarray) -> np.ndarray:
    """Ensure that the image is a 3-channel BGR numpy uint8 array."""
    if image is None or image.size == 0:
        raise ValueError("Image array is empty or None.")

    img = image.copy()
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)

    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif len(img.shape) == 3:
        if img.shape[2] == 1:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
    raise ValueError(f"Unsupported image dimensions: {img.shape}")


def apply_grayscale(image: np.ndarray, keep_3_channels: bool = True) -> np.ndarray:
    """
    Convert a color image into grayscale.
    If keep_3_channels is True, returns (H, W, 3) where R=G=B for pipeline compatibility.
    """
    img = ensure_bgr(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if keep_3_channels:
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    return gray


def apply_gaussian_blur(image: np.ndarray, kernel_size: int = 5, sigma_x: float = 0.0) -> np.ndarray:
    """
    Apply Gaussian Blur to reduce high-frequency noise and detail.
    Kernel size must be an odd positive integer (e.g., 3, 5, 7, ..., 31).
    """
    img = ensure_bgr(image)
    k = max(1, int(kernel_size))
    if k % 2 == 0:
        k += 1
    return cv2.GaussianBlur(img, (k, k), sigma_x)


def apply_median_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    Apply Median Blur to remove salt-and-pepper noise while preserving sharp boundaries.
    Kernel size must be an odd positive integer >= 3.
    """
    img = ensure_bgr(image)
    k = max(3, int(kernel_size))
    if k % 2 == 0:
        k += 1
    return cv2.medianBlur(img, k)


def apply_bilateral_filter(image: np.ndarray, diameter: int = 9, sigma_color: float = 75.0, sigma_space: float = 75.0) -> np.ndarray:
    """
    Apply Bilateral Filter to smooth textures and reduce noise while maintaining sharp edges.
    """
    img = ensure_bgr(image)
    d = max(1, int(diameter))
    sc = max(1.0, float(sigma_color))
    ss = max(1.0, float(sigma_space))
    return cv2.bilateralFilter(img, d, sc, ss)


def apply_sharpen(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """
    Sharpen the image to enhance fine edges and textures.
    Uses unsharp masking and convolution kernel blending based on strength (0.1 to 3.0).
    """
    img = ensure_bgr(image)
    strength = max(0.1, min(5.0, float(strength)))

    # High-boost / unsharp mask formula
    gaussian = cv2.GaussianBlur(img, (0, 0), 2.0)
    sharpened = cv2.addWeighted(img, 1.0 + strength, gaussian, -strength, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def apply_canny_edge(image: np.ndarray, low_thresh: int = 50, high_thresh: int = 150) -> np.ndarray:
    """
    Apply Canny Edge Detection with user-adjustable lower and upper gradient thresholds.
    Returns a 3-channel BGR visualization of the detected edge contours.
    """
    img = ensure_bgr(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    low = max(0, min(255, int(low_thresh)))
    high = max(0, min(255, int(high_thresh)))
    if low > high:
        low, high = high, low

    edges = cv2.Canny(blurred, low, high)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def apply_sepia(image: np.ndarray) -> np.ndarray:
    """
    Apply a warm, vintage Sepia photographic tone matrix.
    """
    img = ensure_bgr(image)
    # Standard Sepia transformation matrix for BGR
    # R' = 0.393 R + 0.769 G + 0.189 B
    # G' = 0.349 R + 0.686 G + 0.168 B
    # B' = 0.272 R + 0.534 G + 0.131 B
    # In BGR order:
    sepia_kernel = np.array([
        [0.131, 0.534, 0.272],
        [0.168, 0.686, 0.349],
        [0.189, 0.769, 0.393]
    ], dtype=np.float32)

    sepia_img = cv2.transform(img, sepia_kernel)
    return np.clip(sepia_img, 0, 255).astype(np.uint8)


def apply_negative(image: np.ndarray) -> np.ndarray:
    """
    Invert image colors (Photographic Negative).
    """
    img = ensure_bgr(image)
    return cv2.bitwise_not(img)


def apply_emboss(image: np.ndarray, intensity: float = 1.0) -> np.ndarray:
    """
    Apply an Emboss convolution kernel to give a 3-dimensional bas-relief effect.
    """
    img = ensure_bgr(image)
    kernel = np.array([
        [-2 * intensity, -1 * intensity, 0],
        [-1 * intensity,  1, 1 * intensity],
        [ 0,  1 * intensity, 2 * intensity]
    ], dtype=np.float32)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    embossed = cv2.filter2D(gray, -1, kernel) + 128
    embossed = np.clip(embossed, 0, 255).astype(np.uint8)
    return cv2.cvtColor(embossed, cv2.COLOR_GRAY2BGR)


def apply_cartoon(image: np.ndarray, bilateral_passes: int = 7, edge_block_size: int = 9) -> np.ndarray:
    """
    Create a stylized cartoon comic effect:
    1. Smooth flat color regions with repeated bilateral filtering.
    2. Extract bold outline edges using median blur and adaptive thresholding.
    3. Composite color and edge mask using bitwise AND.
    """
    img = ensure_bgr(image)

    # 1. Bilateral filtering for cartoon color abstraction
    color = img.copy()
    # Downsample using pyramid to accelerate bilateral filter on large images
    h, w = color.shape[:2]
    num_down = 1 if (w > 800 or h > 800) else 0

    for _ in range(num_down):
        color = cv2.pyrDown(color)

    passes = max(2, min(10, int(bilateral_passes)))
    for _ in range(passes):
        color = cv2.bilateralFilter(color, d=9, sigmaColor=9.0, sigmaSpace=7.0)

    for _ in range(num_down):
        color = cv2.pyrUp(color)

    # Resize back to exact original dimensions if pyramid introduced off-by-one
    if color.shape[:2] != (h, w):
        color = cv2.resize(color, (w, h), interpolation=cv2.INTER_LINEAR)

    # 2. Generate sketch edge mask
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, 7)

    block_size = max(3, int(edge_block_size))
    if block_size % 2 == 0:
        block_size += 1

    edges = cv2.adaptiveThreshold(
        gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, block_size, 9
    )
    edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    # 3. Composite cartoon image
    cartoon = cv2.bitwise_and(color, edges_color)
    return cartoon


def apply_histogram_equalization(image: np.ndarray) -> np.ndarray:
    """
    Apply Histogram Equalization to expand dynamic contrast.
    Supports both Grayscale and Color images (via YCrCb luminance channel or CLAHE).
    """
    img = ensure_bgr(image)

    # Convert to YCrCb color space so we only equalize the Luminance (Y) channel
    # This prevents artificial color shifting while significantly boosting contrast
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)

    # Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) for natural enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    y_eq = clahe.apply(y)

    merged = cv2.merge([y_eq, cr, cb])
    return cv2.cvtColor(merged, cv2.COLOR_YCrCb2BGR)
