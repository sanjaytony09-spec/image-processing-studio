"""
Automated unit verification for Image Processing Toolkit core modules.
"""

import os
import sys
import numpy as np
import cv2

# Windows console encoding safeguard
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure root directory is on path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from modules.image_io import load_image, save_image, bgr_to_pil, pil_to_bgr
from modules.image_processing import (
    apply_grayscale,
    apply_gaussian_blur,
    apply_median_blur,
    apply_bilateral_filter,
    apply_sharpen,
    apply_canny_edge,
    apply_sepia,
    apply_negative,
    apply_emboss,
    apply_cartoon,
    apply_histogram_equalization
)
from modules.image_transformations import (
    rotate_image,
    flip_image,
    resize_image,
    crop_image,
    adjust_brightness_contrast
)
from modules.histogram import generate_histogram_figure


def run_tests():
    print("Testing Image Processing Toolkit Core Modules...")

    # Create synthetic test image (color gradient + shapes)
    h, w = 300, 400
    test_img = np.zeros((h, w, 3), dtype=np.uint8)
    # Gradient
    for i in range(h):
        for j in range(w):
            test_img[i, j] = [j % 256, (i * 2) % 256, (i + j) % 256]
    # Draw shapes
    cv2.circle(test_img, (200, 150), 60, (255, 255, 0), -1)
    cv2.rectangle(test_img, (50, 50), (120, 180), (0, 0, 255), -1)
    cv2.putText(test_img, "TEST", (130, 260), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

    os.makedirs("samples", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    sample_path = os.path.join("samples", "sample_test.png")
    save_image(test_img, sample_path)
    print("[PASS] save_image passed")

    loaded_img, meta = load_image(sample_path)
    assert loaded_img.shape == (h, w, 3), f"Shape mismatch: {loaded_img.shape}"
    assert meta["width"] == w and meta["height"] == h
    print("[PASS] load_image & metadata passed")

    # Conversions
    pil_img = bgr_to_pil(loaded_img)
    back_bgr = pil_to_bgr(pil_img)
    assert back_bgr.shape == loaded_img.shape
    print("[PASS] bgr_to_pil and pil_to_bgr passed")

    # Filters
    gray = apply_grayscale(loaded_img)
    assert gray.shape == (h, w, 3)
    print("[PASS] apply_grayscale passed")

    gblur = apply_gaussian_blur(loaded_img, kernel_size=7)
    assert gblur.shape == loaded_img.shape
    print("[PASS] apply_gaussian_blur passed")

    mblur = apply_median_blur(loaded_img, kernel_size=5)
    assert mblur.shape == loaded_img.shape
    print("[PASS] apply_median_blur passed")

    bilat = apply_bilateral_filter(loaded_img, diameter=7)
    assert bilat.shape == loaded_img.shape
    print("[PASS] apply_bilateral_filter passed")

    sharp = apply_sharpen(loaded_img, strength=1.5)
    assert sharp.shape == loaded_img.shape
    print("[PASS] apply_sharpen passed")

    canny = apply_canny_edge(loaded_img, low_thresh=50, high_thresh=150)
    assert canny.shape == loaded_img.shape
    print("[PASS] apply_canny_edge passed")

    sepia = apply_sepia(loaded_img)
    assert sepia.shape == loaded_img.shape
    print("[PASS] apply_sepia passed")

    negative = apply_negative(loaded_img)
    assert negative.shape == loaded_img.shape
    print("[PASS] apply_negative passed")

    emboss = apply_emboss(loaded_img, intensity=1.2)
    assert emboss.shape == loaded_img.shape
    print("[PASS] apply_emboss passed")

    cartoon = apply_cartoon(loaded_img)
    assert cartoon.shape == loaded_img.shape
    print("[PASS] apply_cartoon passed")

    eq = apply_histogram_equalization(loaded_img)
    assert eq.shape == loaded_img.shape
    print("[PASS] apply_histogram_equalization passed")

    # Transformations
    r90 = rotate_image(loaded_img, 90)
    assert r90.shape == (w, h, 3)
    r180 = rotate_image(loaded_img, 180)
    assert r180.shape == (h, w, 3)
    r270 = rotate_image(loaded_img, 270)
    assert r270.shape == (w, h, 3)
    print("[PASS] rotate_image (90, 180, 270) passed")

    fliph = flip_image(loaded_img, 'horizontal')
    flipv = flip_image(loaded_img, 'vertical')
    assert fliph.shape == loaded_img.shape and flipv.shape == loaded_img.shape
    print("[PASS] flip_image (H & V) passed")

    resized = resize_image(loaded_img, 200, 150)
    assert resized.shape == (150, 200, 3)
    print("[PASS] resize_image passed")

    cropped = crop_image(loaded_img, 20, 20, 100, 80)
    assert cropped.shape == (60, 80, 3)
    print("[PASS] crop_image passed")

    bc = adjust_brightness_contrast(loaded_img, brightness=20, contrast=15)
    assert bc.shape == loaded_img.shape
    print("[PASS] adjust_brightness_contrast passed")

    # Histogram
    fig_color = generate_histogram_figure(loaded_img, mode='color')
    fig_gray = generate_histogram_figure(loaded_img, mode='gray')
    assert fig_color is not None and fig_gray is not None
    print("[PASS] generate_histogram_figure (color & gray) passed")

    print("\nALL MODULE TESTS PASSED SUCCESSFULLY! 100% OK")


if __name__ == '__main__':
    run_tests()
