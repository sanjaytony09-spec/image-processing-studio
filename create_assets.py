"""
Generates modern app assets and sample demonstration images for the Image Processing Toolkit.
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw

os.makedirs("assets", exist_ok=True)
os.makedirs("samples", exist_ok=True)

# 1. Generate App Icon (assets/app_icon.png)
icon_size = 256
icon_img = np.zeros((icon_size, icon_size, 4), dtype=np.uint8)

# Create a rich modern rounded gradient icon with a camera lens / magic wand / aperture
for y in range(icon_size):
    for x in range(icon_size):
        # Radial gradient from indigo (#4f46e5) to deep purple (#1e1b4b)
        dist = np.sqrt((x - icon_size // 2) ** 2 + (y - icon_size // 2) ** 2) / (icon_size * 0.7)
        dist = min(1.0, dist)
        r = int(79 * (1 - dist) + 30 * dist)
        g = int(70 * (1 - dist) + 27 * dist)
        b = int(229 * (1 - dist) + 75 * dist)
        icon_img[y, x] = [b, g, r, 255]

# Convert to PIL for anti-aliased drawing
pil_icon = Image.fromarray(cv2.cvtColor(icon_img, cv2.COLOR_BGRA2RGBA))
draw = ImageDraw.Draw(pil_icon)

# Draw stylized aperture / lens rings
center = (128, 128)
draw.ellipse((38, 38, 218, 218), outline=(99, 102, 241, 240), width=6)
draw.ellipse((58, 58, 198, 198), fill=(24, 28, 42, 230), outline=(129, 140, 248, 255), width=4)
draw.ellipse((85, 85, 171, 171), fill=(49, 46, 129, 240), outline=(165, 180, 252, 220), width=3)
draw.ellipse((105, 105, 151, 151), fill=(99, 102, 241, 255))
# Glint highlight
draw.ellipse((75, 75, 105, 105), fill=(255, 255, 255, 180))

pil_icon.save(os.path.join("assets", "app_icon.png"), format="PNG")
print("Generated assets/app_icon.png")

# 2. Sample 1: Scenic Landscape (samples/sample_landscape.jpg)
w, h = 800, 600
scenic = np.zeros((h, w, 3), dtype=np.uint8)

# Sky gradient (sky blue to warm sunset orange)
for y in range(h // 2):
    t = y / (h // 2)
    scenic[y, :] = [int(240 * (1 - t) + 120 * t), int(180 * (1 - t) + 160 * t), int(70 * (1 - t) + 245 * t)]

# Distant Mountains (triangular polygons)
mountain_pts = np.array([[0, 360], [160, 160], [320, 360], [480, 190], [640, 370], [800, 220], [800, 360], [0, 360]], np.int32)
cv2.fillPoly(scenic, [mountain_pts], (140, 110, 90))
mountain_shadow = np.array([[160, 160], [320, 360], [480, 190], [640, 370], [800, 220], [800, 360], [160, 360]], np.int32)
cv2.fillPoly(scenic, [mountain_shadow], (110, 85, 70))

# Sun
cv2.circle(scenic, (650, 130), 45, (80, 220, 255), -1)

# Water lake in foreground with reflections
for y in range(h // 2, h):
    t = (y - h // 2) / (h // 2)
    # Lake gradient
    b = int(180 * (1 - t) + 90 * t)
    g = int(140 * (1 - t) + 70 * t)
    r = int(50 * (1 - t) + 20 * t)
    scenic[y, :] = [b, g, r]

# Ripple lines on water
for y in range(h // 2 + 30, h, 25):
    cv2.line(scenic, (50, y), (750, y), (190, 160, 90), 2)

# Pine trees on shore
def draw_pine(img, x, y, scale=1.0):
    for i in range(3):
        pts = np.array([
            [x, int(y - 50 * scale + i * 15 * scale)],
            [int(x - 25 * scale - i * 5 * scale), int(y - 15 * scale + i * 20 * scale)],
            [int(x + 25 * scale + i * 5 * scale), int(y - 15 * scale + i * 20 * scale)]
        ], np.int32)
        cv2.fillPoly(img, [pts], (25, 80, 35))
    cv2.rectangle(img, (int(x - 4 * scale), int(y + 25 * scale)), (int(x + 4 * scale), int(y + 40 * scale)), (20, 45, 60), -1)

draw_pine(scenic, 90, 340, 1.4)
draw_pine(scenic, 150, 355, 1.1)
draw_pine(scenic, 210, 345, 1.3)
draw_pine(scenic, 720, 350, 1.5)

cv2.imwrite(os.path.join("samples", "sample_landscape.jpg"), scenic, [cv2.IMWRITE_JPEG_QUALITY, 95])
print("Generated samples/sample_landscape.jpg")

# 3. Sample 2: Geometric & Contrast Artwork (samples/sample_geometric.png)
w2, h2 = 700, 500
geom = np.zeros((h2, w2, 3), dtype=np.uint8)
geom[:] = (35, 30, 30) # Dark sleek background

# Vibrant neon geometric shapes
cv2.circle(geom, (220, 250), 120, (235, 130, 40), -1)
cv2.circle(geom, (350, 220), 100, (60, 220, 240), -1)
cv2.rectangle(geom, (380, 180), (580, 380), (180, 70, 240), -1)
cv2.ellipse(geom, (500, 320), (140, 60), 30, 0, 360, (70, 220, 100), -1)

# Overlay crisp typography
cv2.putText(geom, "IMAGE TOOLKIT", (80, 110), cv2.FONT_HERSHEY_DUPLEX, 1.6, (250, 250, 250), 3, cv2.LINE_AA)
cv2.putText(geom, "College Demo Test Pattern", (85, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 190, 205), 2, cv2.LINE_AA)

cv2.imwrite(os.path.join("samples", "sample_geometric.png"), geom)
print("Generated samples/sample_geometric.png")

# 4. Sample 3: Noisy Image (samples/sample_noisy.png)
noisy = scenic.copy()
# Add Salt-and-Pepper noise
num_noise = int(0.04 * h * w)
for _ in range(num_noise):
    ry = np.random.randint(0, h)
    rx = np.random.randint(0, w)
    noisy[ry, rx] = (255, 255, 255) if np.random.rand() > 0.5 else (0, 0, 0)

cv2.imwrite(os.path.join("samples", "sample_noisy.png"), noisy)
print("Generated samples/sample_noisy.png")
