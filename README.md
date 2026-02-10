# EpiGimp

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-GPLv3-green)
![Build Status](https://img.shields.io/github/actions/workflow/status/YourUsername/EpiGimp/build-shared.yml)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

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

**Data Integrity**:
- Native Format: Save projects as `.epigimp` binary files to preserve layers and metadata.
- Metadata Editor: View and edit EXIF, IPTC, and XMP data standards.
- Export: Support for industry-standard formats (PNG, JPG, TIFF).

## Architecture
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

## Documentation

- Serialization specification of `.epigimp`: [docs/FILE_FORMAT.md](docs/FILE_FORMAT.md)
- Project specification of **EpiGimp**: [docs/PROJECT_SPECIFICATION_EN.md](docs/PROJECT_SPECIFICATION_EN.md)
- CI/CD specification: [docs/CI_CD.md]([docs/CI_CD.md])
- Shortcuts specification: [docs/SHORTCUTS.md]([docs/SHORTCUTS.md])

## Development & Quality Assurance

We adhere to strict code quality standards.

- **Testing**: Run the full test suite with pytest.
```bash
    pytest tests/ --cov=EpiGimp
```

- **Linting**: We use flake8 for linting and black for formatting.
```bash
    flake8 .
    black . --check
```

- **Type Checking**: Static analysis via mypy.
```bash
mypy EpiGimp/
```

## Contributing
Please refer to [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines on:

- GitFlow branching strategy (main, dev, feature/).
- Coding standards (PEP 8, Type Hinting).
- Commit message conventions.

## Roadmap & Changelog

Check our [Github Project](https://github.com/users/Tipbs/projects/1) and our [Milestones](https://github.com/Tipbs/EpiGimp/milestones) for a roadmap.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE) file for details.

## Authors

- DaiC - Initial work

EpiGimp is currently in active development.
