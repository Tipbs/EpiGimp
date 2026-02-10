# EpiGimp

EpiGimp is a lightweight, GIMP-like raster image editor built with Python and PySide6 (Qt). It features a layer-based architecture, essential drawing tools, and advanced metadata editing capabilities, serving as a robust prototype for image manipulation.

## Key Features

**Layer-Based Editing:**
- Full support for multiple layers with visibility toggles.
- Layer reordering (move up/down), locking, and renaming.
- Opacity and Blending Mode support (Normal, Multiply, Screen, Overlay, etc.).

**Drawing Tools:**
- Brush: Customizable size and color.
- Eraser: Alpha-channel erasing.
- Extensible tool system for future additions.

**Image Adjustments:**
- Color Temperature: Adjust Kelvin values (e.g., Candle 1850K to Daylight 5500K) with real-time preview.
- Transformations: Flip (Horizontal/Vertical) and Rotate (90°, 180°).

**Project Management:**
- Custom File Format: Save projects as .epigimp (preserves layers and metadata).
- Export: Support for PNG, JPG, BMP, TIFF, and GIF via OpenCV.
- Metadata: View and Edit EXIF, IPTC, and XMP data.

**User Interface:**
- Dockable widgets (Layers, Toolbox).
- Configurable settings (Themes, Shortcuts).
- Startup Welcome Screen with recent file history.

## 🛠️ Architecture
The application is structured to separate core logic from the UI:

- `EpiGimp/core/`: Handles the business logic.

    - `canva.py`: Manages the image composition and stack of layers.

    - `layer.py`: Represents individual image layers (NumPy arrays).

    - `fileio/`: Handles loading/saving `.epigimp` binary files and standard images.

- `EpiGimp/ui/`: PySide6 widgets and windows.

    - `widgets/`: Reusable components like the Canvas, Layer List, and Toolbox.

    - `dialogs/`: Complex interactions (New Image, Settings, Color Temp, Metadata).

- `EpiGimp/tools/`: Logic for individual tools (Brush, Eraser) following a BaseTool abstract class.

## Getting Started

**Prerequisites**

- Python 3.10 or higher.
- Virtual environment recommended.

**Installation**

1. **Clone the repository:**

```bash
git clone https://github.com/YourUsername/EpiGimp.git
cd EpiGimp
```

2. **Set up a virtual environment:**

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

*Dependencies include: PySide6, numpy, opencv-python, pillow, pytest.*

**Running the Application**

Execute the main entry point:
```bash
python main.py
```

## ⌨️ Shortcuts

Customize these in Settings > Shortcuts.
| New Image              | `Ctrl+N`       |
|------------------------|----------------|
| Open File (in Project) | `Ctrl+O`       |
| Open File (New Tab)    | `Ctrl+Shift+O` |
| Save Project           | `Ctrl+S`       |
| Load Project           | `Ctrl+L`       |
| Export Image           | `Ctrl+E`       |
| Toggle Fullscreen      | `F11`          |

## Development & Testing

We use **pytest** for unit testing core logic.

To run the test suite:
```bash
pytest tests/
```

**Contributing**
Please refer to [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines on:

- GitFlow branching strategy (main, dev, feature/).
- Coding standards (PEP 8, Type Hinting).
- Commit message conventions.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE) file for details.

## Authors

- DaiC - Initial work

EpiGimp is currently in active development.
