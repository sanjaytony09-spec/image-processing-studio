# Image Processing Toolkit

An interactive desktop application for digital image processing, computer vision transformations, visual enhancement, and intensity analysis developed with Python, OpenCV, Tkinter, Pillow, NumPy, and Matplotlib.

---

## 1. Project Title
**Image Processing Toolkit: An Interactive Computer Vision Desktop Environment**

---

## 2. Abstract
The **Image Processing Toolkit** is an educational and practical desktop software suite designed to make classical computer vision and digital image processing concepts accessible, visual, and interactive. Digital image processing is a fundamental subject in computer science and multimedia engineering, yet beginners often struggle to bridge the gap between mathematical matrix transformations and their real-time visual manifestations. This toolkit provides a modern graphical user interface (GUI) allowing users to load images in multiple formats, perform spatial filtering, non-linear noise reduction, frequency-domain and kernel sharpening, multi-stage edge detection, artistic stylization, geometric transformations, and photometric enhancements. It incorporates real-time side-by-side comparative visualization, full-resolution non-destructive rendering, interactive parameter tuning, an undo/redo state history stack, multi-channel histogram distribution analysis, and automated batch processing.

---

## 3. Problem Statement
In digital image processing courses and introductory computer vision labs, students often encounter algorithms strictly via command-line Python scripts or static Jupyter Notebook cells. This presents several challenges:
1. **Lack of Instant Feedback:** Adjusting parameters (such as kernel sizes, filter sigmas, or edge thresholds) requires manual script edits and repeated re-execution.
2. **Abstract Spatial Concepts:** Students cannot intuitively observe the trade-offs between noise suppression and edge preservation (e.g., Gaussian Blur vs. Bilateral Filtering).
3. **Destructive Processing:** Novice scripts frequently overwrite image arrays in memory or downsample the original image permanently, causing loss of fidelity.
4. **Platform Discrepancies:** Standard OpenCV commands (`cv2.imread`, `cv2.imwrite`) fail silently on Windows systems when paths contain non-ASCII characters or spaces.

The Image Processing Toolkit addresses these problems by providing an integrated, robust, and beginner-friendly environment with real-time feedback, non-destructive workflows, and an intuitive graphical interface.

---

## 4. Objectives
- **Interactive Exploration:** Provide an intuitive GUI to manipulate images with immediate visual feedback.
- **Comprehensive Filter Suite:** Implement core linear and non-linear filtering algorithms, edge detectors, and color manipulations using OpenCV and NumPy.
- **Side-by-Side Comparison:** Enable clear visual comparison between the original input and the processed output.
- **Robust State Management:** Implement a multi-level Undo/Redo history stack to allow safe experimentation.
- **High-Fidelity Preservation:** Maintain the original image resolution during display resizing and saving.
- **Statistical Insight:** Visualize RGB and Grayscale pixel intensity distributions using integrated Matplotlib histograms.
- **Batch Automation:** Allow bulk filtering across multiple images with progress reporting.

---

## 5. Technologies Used
- **Python (3.8+ / 3.10+ / 3.14+):** Core programming language.
- **OpenCV (`opencv-python` / `cv2`):** Primary computer vision and array-processing library used for convolutions, color spaces, transformations, and filtering.
- **Tkinter (`tkinter` & `ttk`):** Standard Python GUI library providing cross-platform window management, canvases, and widgets.
- **Pillow (`PIL`):** Bridge for converting OpenCV BGR arrays to Tkinter-compatible `PhotoImage` representations and managing high-quality thumbnail downsampling.
- **NumPy (`numpy`):** High-performance multi-dimensional array operations, matrix conversions, and memory buffers.
- **Matplotlib (`matplotlib`):** Statistical data visualization library used to compute and render pixel intensity histograms embedded into Tkinter.

---

## 6. System Requirements

### Hardware Requirements
- **Processor:** 1.6 GHz or faster dual-core x86/x64 CPU.
- **RAM:** Minimum 2 GB (4 GB or more recommended for high-resolution images).
- **Disk Space:** Approximately 250 MB free disk space for dependencies and assets.
- **Display Resolution:** 1280 × 720 or higher recommended.

### Software Requirements
- **Operating System:** Windows 10 / Windows 11 (also compatible with macOS and Linux).
- **Python Environment:** Python 3.8 to Python 3.14 (with Tkinter enabled).

---

## 7. Installation Instructions

### Windows (PowerShell or Command Prompt)
1. Open PowerShell or Command Prompt.
2. Navigate to the project root directory:
   ```powershell
   cd "c:\Users\Tony\Desktop\Image processing"
   ```
3. Install the required dependencies:
   ```powershell
   py -m pip install -r requirements.txt
   ```
   *(Alternatively, if your system uses `python`: `python -m pip install -r requirements.txt`)*

---

## 8. Instructions for Running the Application

### Option A: Using the Windows Batch Launcher (Easiest)
Double-click `run.bat` in the project folder, or run:
```cmd
run.bat
```

### Option B: Using the Python Launcher (`py`)
```powershell
py main.py
```

### Option C: Using Standard Python
```powershell
python main.py
```

### Running the Core Verification Tests
To verify all computer vision modules, transformations, and format conversions without the GUI:
```powershell
py test_core.py
```
To verify the headless GUI lifecycle:
```powershell
py test_gui.py
```

---

## 9. Description of Image Processing Techniques

### 1. Grayscale Conversion
- **Concept:** Converts a 3-channel RGB/BGR image into a single-channel luminance intensity representation.
- **Formula:** 
  $$Y = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$$
- **Use Case:** Simplifies feature detection, reduces computational complexity, and acts as a pre-processing step for edge detection.

### 2. Gaussian Blur
- **Concept:** A linear low-pass filter that convolves the image with a 2D Gaussian bell-curve kernel.
- **Kernel Weights:**
  $$G(x, y) = \frac{1}{2\pi\sigma^2} e^{-\frac{x^2 + y^2}{2\sigma^2}}$$
- **Use Case:** Attenuates high-frequency noise and details smoothly while avoiding boxy artifacts.

### 3. Median Blur
- **Concept:** A non-linear spatial filter that replaces each central pixel with the median value of all pixels in its local neighborhood window.
- **Use Case:** Outstanding effectiveness at eliminating impulse noise ("salt-and-pepper" noise) without blurring sharp step-edges.

### 4. Bilateral Filtering
- **Concept:** An advanced non-linear smoothing filter that combines spatial geometric closeness with photometric range radiometric similarity.
- **Formula:** Weights pixels both by Euclidean distance from the center and by color intensity difference.
- **Use Case:** Smooths surface textures and noise while preserving crisp boundary edges (ideal for skin beautification and cartoon stylization).

### 5. Sharpening (Unsharp Masking & Kernel Convolution)
- **Concept:** Amplifies high-frequency differences (edges and fine textures) by subtracting a blurred version of the image from the original or applying a Laplacian high-pass kernel:
  $$K = \begin{bmatrix} 0 & -1 & 0 \\ -1 & 5 & -1 \\ 0 & -1 & 0 \end{bmatrix}$$
- **Use Case:** Restores lost definition in soft photographs and highlights intricate textures.

### 6. Canny Edge Detection
- **Concept:** A multi-stage edge detection algorithm:
  1. Gaussian noise filtering.
  2. Intensity gradient calculation via Sobel operators.
  3. Non-Maximum Suppression (thinning candidate edge pixels).
  4. Hysteresis thresholding with dual thresholds ($T_{low}$ and $T_{high}$) to link continuous contours and discard isolated weak responses.
- **Use Case:** Structural segmentation, object outline identification, and medical image boundary analysis.

### 7. Sepia Filter
- **Concept:** A linear photometric color matrix multiplication that imparts a nostalgic, warm reddish-brown tone reminiscent of early 20th-century silver-gelatin prints.
- **Matrix:**
  $$\begin{bmatrix} R' \\ G' \\ B' \end{bmatrix} = \begin{bmatrix} 0.393 & 0.769 & 0.189 \\ 0.349 & 0.686 & 0.168 \\ 0.272 & 0.534 & 0.131 \end{bmatrix} \begin{bmatrix} R \\ G \\ B \end{bmatrix}$$

### 8. Negative Filter
- **Concept:** Inverts image intensities on a per-channel basis:
  $$I'(x, y) = 255 - I(x, y)$$
- **Use Case:** Analyzing inverted X-rays, thermal imagery, or artistic color reversals.

### 9. Emboss Filter
- **Concept:** Computes directional derivatives along the diagonal using a $3 \times 3$ convolution kernel followed by a $+128$ intensity bias:
  $$K = \begin{bmatrix} -2 & -1 & 0 \\ -1 & 1 & 1 \\ 0 & 1 & 2 \end{bmatrix}$$
- **Use Case:** Creates a tactile 3D relief or carved-stone illusion.

### 10. Cartoon Effect
- **Concept:** A compound artistic pipeline:
  1. Repeated bilateral filtering to flatten gradient variations into uniform color cells.
  2. Median blur and adaptive thresholding on grayscale luminance to extract strong black sketch outlines.
  3. Bitwise masking (`cv2.bitwise_and`) combining stylized colors and dark outlines.

### 11. Histogram Equalization (Contrast Enhancement)
- **Concept:** Re-distributes pixel intensities across the full dynamic range [0, 255]. For color images, the image is converted to the **YCrCb** color space, and **CLAHE** (Contrast Limited Adaptive Histogram Equalization) is applied solely to the Luminance (Y) channel before converting back to BGR.
- **Use Case:** Revealing hidden details in underexposed or overexposed photography without distorting chromatic balances.

### 12. Geometric Transformations
- **Rotation:** Exact $90^\circ$, $180^\circ$, and $270^\circ$ transformations using memory-aligned matrix manipulation (`cv2.rotate`).
- **Flipping:** Horizontal and vertical reflections (`cv2.flip`).
- **Interactive Cropping:** Mouse drag-and-drop bounding box mapping from screen coordinates back to full-resolution image arrays.
- **Resizing:** High-quality interpolation (`cv2.INTER_AREA` for downsampling; `cv2.INTER_CUBIC` for upsampling) with aspect-ratio preservation.

---

## 10. System Architecture & Workflow

```
+-------------------------------------------------------------------------+
|                               USER INTERFACE                            |
|  [Header Actions]  [Left Sidebar Tools]  [Parameter Bar]  [Status Bar]  |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                         APPLICATION CONTROLLER                          |
|                             (main.py)                                   |
|  - Event dispatching                                                    |
|  - Multi-level Undo/Redo stack management                               |
|  - Dynamic canvas coordinate mapping                                    |
|  - Asynchronous / live preview coordination                             |
+---------+-------------------+-------------------+-------------------+---+
          |                   |                   |                   |
          v                   v                   v                   v
+-------------------+ +-------------------+ +-------------------+ +---------------+
|     image_io      | | image_processing  | | image_transforms  | |   histogram   |
|  (load/save/conv) | | (filters/effects) | | (geom/photometric)| | (matplotlib)  |
+-------------------+ +-------------------+ +-------------------+ +---------------+
          |                   |                   |                   |
          +-------------------+-------------------+-------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                       OPENCV & NUMPY ENGINE                             |
|          High-performance matrix algebra and image pipelines            |
+-------------------------------------------------------------------------+
```

---

## 11. Key Features
1. **Side-by-Side Dual Preview:** Live comparison between original and processed images.
2. **Interactive Cropping:** Visual drag marquee on the canvas with coordinates mapped accurately to high-resolution data.
3. **Multi-level Undo / Redo:** Full history tracking up to 25 operations.
4. **Contextual Parameter Bar:** Live sliders for blur intensity, edge thresholds, brightness, contrast, and scaling.
5. **Non-Destructive Scaling:** Canvas previews adapt dynamically on window resize without degrading the original array.
6. **Cross-Platform Format Support:** Handles JPG, JPEG, PNG, BMP, TIFF, and WEBP. Unicode-safe path loading for Windows.
7. **Color & Grayscale Histograms:** Embedded Matplotlib distribution graphs with mean and standard deviation metrics.
8. **Automated Batch Processing:** Bulk directory transformation with progress tracking and real-time execution logs.

---

## 12. Advantages and Limitations

### Advantages
- **Educational Value:** Real-time visual illustration of theoretical DSP and CV algorithms.
- **Robust Error Handling:** File format validation, boundary clamping, and friendly error dialogs.
- **Memory Efficiency:** NumPy arrays are manipulated in-place or copied strictly when pushing to the undo stack.
- **Zero Third-Party GUI Frameworks:** Built with native Tkinter and Pillow—easy to run without complex setups.

### Limitations
- Single-threaded GUI event loop (batch processing very large datasets of 100+ multi-megapixel images can temporarily occupy the thread).
- Extremely large images (e.g., >8000x8000 px) consume higher RAM during recursive undo history storage.

---

## 13. Possible Future Enhancements
- Fast Fourier Transform (FFT) 2D frequency spectrum magnitude visualization.
- Deep-learning-based background removal and super-resolution upscaling (using ONNX Runtime).
- Hough Transform for line and circle detection.
- Morphological operations workbench (Dilation, Erosion, Opening, Closing, Top-Hat).
- GPU acceleration via OpenCL / CUDA.

---

## 14. Conclusion
The **Image Processing Toolkit** provides an end-to-end, functional, and visually appealing solution for computer vision education and digital image analysis. Combining mathematical filtering, interactive transformation tools, statistical histogram evaluation, and bulk automation into an intuitive desktop GUI, it fulfills all requirements for academic demonstrations and laboratory coursework.

---

## 15. College Demonstration Guide

When demonstrating this project to your tutor or evaluator, follow this structured walkthrough:

1. **Launch the Application:**
   Run `run.bat` or `py main.py`. Point out the professional dark UI layout, the header, sidebar, status bar, and side-by-side workspace.
2. **Load a Sample Image:**
   Click **"🖼 Sample Image"** in the top-right header and pick `sample_landscape.jpg` or `sample_noisy.png`. Note how the image details (dimensions, channels, format, file size) automatically populate the status bar.
3. **Demonstrate Smoothing & Noise Reduction:**
   Select `samples/sample_noisy.png`. Choose **"Median Blur"** from the sidebar. Move the slider to 5 px or 7 px and click **"Apply"**. Explain that median filtering eliminates salt-and-pepper noise while preserving the edges of the mountains and trees.
4. **Demonstrate Canny Edge Detection:**
   Select **"Canny Edge Detection"**. Show how adjusting the *Low Threshold* and *High Threshold* sliders in the parameter bar isolates structural contours in real time.
5. **Demonstrate Artistic Cartoon & Sepia Effects:**
   Click **"Cartoon Effect"** to demonstrate bilateral color flattening combined with adaptive threshold sketch lines. Then click **"Sepia Filter"** to show color space matrix transformation.
6. **Demonstrate Undo / Redo:**
   Press `Ctrl+Z` (or click **"Undo"**) several times to step back through previous filters. Then click **"Redo"** to restore them.
7. **Demonstrate Interactive Cropping & Resizing:**
   Click **"Crop Image"**. Drag a rectangle over an area on the processed image card, and click **"Apply"**.
8. **Demonstrate Histogram Analysis:**
   Click **"Image Histogram"** in the sidebar. Toggle between **"RGB Color Channels"** and **"Grayscale Intensity"**. Explain the distribution peaks and contrast spread.
9. **Demonstrate Batch Processing:**
   Click **"Batch Processing"**. Select all images in the `samples/` folder, choose **"Grayscale Filter"**, and click **"Start Batch Processing"**. Show the processed outputs saved into the `output/` folder.
10. **Save Final Output:**
    Click **"💾 Save Image"** and save the high-resolution output in PNG or JPG format.
