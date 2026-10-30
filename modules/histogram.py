"""
Image Histogram Module for Image Processing Toolkit
Generates Matplotlib figure plots for Grayscale and RGB color intensity distributions.
Supports embedding into Tkinter windows via FigureCanvasTkAgg.
"""

import cv2
import numpy as np
import matplotlib
# Use Agg backend for reliable off-screen rendering
matplotlib.use('Agg')
from matplotlib.figure import Figure


def generate_histogram_figure(
    image: np.ndarray,
    mode: str = 'color',
    bg_color: str = '#1e222d',
    text_color: str = '#e0e6ed',
    grid_color: str = '#2d3342'
) -> Figure:
    """
    Generate a styled Matplotlib Figure displaying intensity histograms.

    Args:
        image: BGR or Grayscale numpy array.
        mode: 'color' (RGB channels) or 'gray' (luminance).
        bg_color: Canvas background color hex.
        text_color: Text / ticks color hex.
        grid_color: Grid line color hex.

    Returns:
        matplotlib.figure.Figure instance.
    """
    if image is None or image.size == 0:
        raise ValueError("Cannot plot histogram for an empty image.")

    fig = Figure(figsize=(6.2, 3.8), dpi=100, facecolor=bg_color)
    ax = fig.add_subplot(111)
    ax.set_facecolor(bg_color)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(text_color)
    ax.spines['bottom'].set_color(text_color)
    ax.tick_params(axis='x', colors=text_color, labelsize=9)
    ax.tick_params(axis='y', colors=text_color, labelsize=9)
    ax.grid(True, linestyle='--', alpha=0.4, color=grid_color)
    ax.set_xlim([0, 256])
    ax.set_xlabel('Pixel Intensity (0 - 255)', color=text_color, fontsize=10, labelpad=8)
    ax.set_ylabel('Pixel Count', color=text_color, fontsize=10, labelpad=8)

    # Normalize image to BGR uint8
    img = image
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)

    if mode == 'gray' or len(img.shape) == 2 or (len(img.shape) == 3 and img.shape[2] == 1):
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        mean_val = np.mean(gray)
        std_val = np.std(gray)

        ax.plot(hist, color='#60a5fa', linewidth=1.8, label=f'Grayscale (μ={mean_val:.1f}, σ={std_val:.1f})')
        ax.fill_between(range(256), hist, color='#60a5fa', alpha=0.25)
        ax.set_title("Grayscale Intensity Histogram", color=text_color, fontsize=11, fontweight='bold', pad=12)
    else:
        # RGB Color Histogram
        # In OpenCV BGR: 0=Blue, 1=Green, 2=Red
        colors_info = [
            (2, 'Red', '#ef4444'),
            (1, 'Green', '#22c55e'),
            (0, 'Blue', '#3b82f6')
        ]

        for channel_idx, channel_name, hex_code in colors_info:
            hist = cv2.calcHist([img], [channel_idx], None, [256], [0, 256]).flatten()
            mean_val = np.mean(img[:, :, channel_idx])
            ax.plot(hist, color=hex_code, linewidth=1.6, label=f'{channel_name} (μ={mean_val:.1f})', alpha=0.9)
            ax.fill_between(range(256), hist, color=hex_code, alpha=0.15)

        ax.set_title("RGB Color Channels Histogram", color=text_color, fontsize=11, fontweight='bold', pad=12)

    legend = ax.legend(facecolor=bg_color, edgecolor=grid_color, fontsize=9, loc='upper right')
    for text in legend.get_texts():
        text.set_color(text_color)

    fig.tight_layout()
    return fig
