"""
Image I/O Module for Image Processing Toolkit
Handles robust image loading, format conversions (OpenCV BGR <-> PIL RGB),
saving to various formats, and thumbnail generation for display without
altering full-resolution data.
"""

import os
from typing import Tuple, Dict, Any
import cv2
import numpy as np
from PIL import Image, ImageTk

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Retrieve detailed file system metadata for an image file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_size_bytes = os.path.getsize(file_path)
    if file_size_bytes < 1024:
        size_str = f"{file_size_bytes} B"
    elif file_size_bytes < 1024 * 1024:
        size_str = f"{file_size_bytes / 1024:.2f} KB"
    else:
        size_str = f"{file_size_bytes / (1024 * 1024):.2f} MB"

    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].upper().replace('.', '')
    if not ext:
        ext = "UNKNOWN"

    return {
        "filename": filename,
        "file_path": file_path,
        "file_size_bytes": file_size_bytes,
        "file_size_str": size_str,
        "file_format": ext
    }


def load_image(file_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Load an image from disk using OpenCV.
    Uses np.fromfile + cv2.imdecode to reliably handle non-ASCII/Unicode paths on Windows.

    Returns:
        Tuple of (bgr_image_array, metadata_dict)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file does not exist: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format '{ext}'. Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # Read binary bytes and decode with OpenCV to avoid Windows path encoding issues
    try:
        data = np.fromfile(file_path, dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    except Exception as e:
        raise IOError(f"Failed to read image data from {file_path}: {e}")

    if image is None:
        raise ValueError(f"Unable to decode image file. File may be corrupted or not a valid image: {file_path}")

    # Handle 4-channel BGRA images by converting to 3-channel BGR
    if len(image.shape) == 3 and image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    elif len(image.shape) == 2:
        # 1-channel grayscale - keep it or convert to 3-channel for standard operations
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    height, width = image.shape[:2]
    channels = image.shape[2] if len(image.shape) == 3 else 1

    metadata = get_file_info(file_path)
    metadata["width"] = width
    metadata["height"] = height
    metadata["channels"] = channels
    metadata["dtype"] = str(image.dtype)

    return image, metadata


def save_image(image: np.ndarray, file_path: str, quality: int = 95) -> str:
    """
    Save the full-resolution processed image to disk.
    Uses cv2.imencode + tofile for cross-platform/Unicode safety.

    Args:
        image: Numpy array of the image (BGR or Grayscale).
        file_path: Destination path with file extension.
        quality: Compression quality for JPEG/WEBP (1-100).

    Returns:
        Destination file path.
    """
    if image is None or image.size == 0:
        raise ValueError("Cannot save an empty or invalid image array.")

    ext = os.path.splitext(file_path)[1].lower()
    if not ext:
        ext = ".png"
        file_path += ext

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported format '{ext}' for saving. Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    # Ensure output directory exists
    output_dir = os.path.dirname(os.path.abspath(file_path))
    os.makedirs(output_dir, exist_ok=True)

    # Encode parameters
    encode_params = []
    if ext in ('.jpg', '.jpeg'):
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), max(1, min(100, quality))]
    elif ext == '.webp':
        encode_params = [int(cv2.IMWRITE_WEBP_QUALITY), max(1, min(100, quality))]
    elif ext == '.png':
        encode_params = [int(cv2.IMWRITE_PNG_COMPRESSION), 4]

    # Ensure image values are valid uint8
    if image.dtype != np.uint8:
        image_to_save = np.clip(image, 0, 255).astype(np.uint8)
    else:
        image_to_save = image

    success, encoded_img = cv2.imencode(ext, image_to_save, encode_params)
    if not success:
        raise IOError(f"OpenCV failed to encode image into format '{ext}'.")

    encoded_img.tofile(file_path)
    return file_path


def bgr_to_pil(bgr_image: np.ndarray) -> Image.Image:
    """
    Convert an OpenCV BGR (or 1-channel Grayscale) numpy array to a PIL Image in RGB mode.
    """
    if bgr_image is None or bgr_image.size == 0:
        raise ValueError("Cannot convert an empty image to PIL.")

    # Normalize dtype to uint8 if float or int32
    if bgr_image.dtype != np.uint8:
        processed = np.clip(bgr_image, 0, 255).astype(np.uint8)
    else:
        processed = bgr_image

    if len(processed.shape) == 2:
        # Grayscale
        return Image.fromarray(processed, mode='L').convert('RGB')
    elif len(processed.shape) == 3:
        if processed.shape[2] == 3:
            rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
            return Image.fromarray(rgb, mode='RGB')
        elif processed.shape[2] == 4:
            rgba = cv2.cvtColor(processed, cv2.COLOR_BGRA2RGBA)
            return Image.fromarray(rgba, mode='RGBA').convert('RGB')
        elif processed.shape[2] == 1:
            return Image.fromarray(processed[:, :, 0], mode='L').convert('RGB')

    raise ValueError(f"Unsupported image shape for conversion: {processed.shape}")


def pil_to_bgr(pil_image: Image.Image) -> np.ndarray:
    """
    Convert a PIL Image to OpenCV BGR numpy array.
    """
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    rgb_array = np.array(pil_image)
    return cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)


def resize_for_display(bgr_image: np.ndarray, max_w: int, max_h: int) -> Tuple[ImageTk.PhotoImage, int, int]:
    """
    Generate an aspect-ratio-preserved Tkinter-compatible PhotoImage for GUI preview
    without altering the underlying full-resolution image.

    Returns:
        Tuple of (PhotoImage, display_width, display_height)
    """
    if bgr_image is None or bgr_image.size == 0:
        raise ValueError("Cannot resize empty image for display.")

    pil_img = bgr_to_pil(bgr_image)
    orig_w, orig_h = pil_img.size

    if max_w <= 10 or max_h <= 10:
        max_w, max_h = 300, 300

    # Compute scale factor
    scale = min(max_w / orig_w, max_h / orig_h)
    new_w = max(1, int(orig_w * scale))
    new_h = max(1, int(orig_h * scale))

    resized_pil = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    photo_image = ImageTk.PhotoImage(resized_pil)

    return photo_image, new_w, new_h
