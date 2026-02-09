# Contributing to EpiGimp

First off, thank you for considering contributing to EpiGimp!

This document outlines the development standards and workflows for the EpiGimp project. As a 2-person team working on a tight 3-month deadline, strictly following these guidelines is crucial to avoid "merge hell" and ensure code quality.

### 1. Getting Started

#### **Prerequisites**
- **Python:** 3.10 or higher
- **Git:** Latest version

#### **Installation**

**1.Clone the repository:**

```
git clone [https://github.com/YourUsername/EpiGimp.git](https://github.com/YourUsername/EpiGimp.git)
cd EpiGimp
```

**2. Create a Virtual Environment:**

```
# Windows
python -m venv venv
.\venv\Scripts\activate
# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```


**3.Install Dependencies:**

```
pip install -r requirements.txt
```

**4.Verify Setup: Run the application to ensure it launches:**

```
python app.py
```

### 2. Development Workflow (GitFlow)

We use a strict GitFlow branching strategy.

**Branches**
- main: 🔴 Production Ready. Do not touch. This branch contains only stable releases.
- dev: 🟡 Integration Branch. All feature branches merge here. This is the "Edge" version of the app.
- feature/<name>: 🟢 Your Workspace. Create a new branch for every task.

**The Process**

1. **Sync Up**: Always pull the latest dev before starting.

```
git checkout dev
git pull origin dev
```

2. **Branch Out**: Create a specific branch for your task.

- Naming Convention: feature/short-description (e.g., feature/brush-tool, feature/layer-opacity).
- For bugs: fix/bug-name (e.g., fix/crash-on-save).

```
git checkout -b feature/my-new-feature
```

3. **Commit Often**: Save your work locally.

4. **Push**: Push your branch to GitHub.

```
git push origin feature/my-new-feature
```

**Commit Messages**

We follow the Conventional Commits specification to make our history readable:

- `feat: description` (New feature)
- `fix: description` (Bug fix)
- `docs: description` (Documentation changes)
- `style: description` (Formatting, missing semi colons, etc; no production code change)
- `refactor: description` (Refactoring production code, e.g. renaming a variable)
- `test: description` (Adding missing tests, refactoring tests)

Example: `feat: implement gaussian blur using opencv`

### 3. Coding Standards

To maintain a professional codebase, we enforce the following rules.

**Style Guide**

- PEP 8: All code must adhere to PEP 8.
- Linting: Run flake8 before submitting a PR.
```
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

**Type Hinting (Mandatory)**

We use Python 3.10+ type hints for all function arguments and return values. This helps us catch bugs early and understand data flow between numpy and PySide.

**Bad**:
```
def add_layer(self, layer):
    self.layers.append(layer)
```
**Good**:

```
from core.layer import Layer

def add_layer(self, layer: Layer) -> None:
    """Adds a new layer to the top of the stack."""
    self.layers.append(layer)
```

**Docstrings**

Use **Google Style** docstrings for all classes and public methods.

```
def resize_canvas(self, width: int, height: int) -> None:
    """
    Resizes the main canvas.

    Args:
        width (int): New width in pixels.
        height (int): New height in pixels.
    """
    pass
```

**Imports**

Organize imports in the following order:

1. Standard Library (e.g., sys, os)
2. Third-party Libraries (numpy, cv2, PySide6, pillow)
3. Local Application Imports (core.canva, ui.widgets)

### 4. Testing

We use **pytest** for testing core logic.

- **Unit Tests**: Located in `tests/`.
- **Requirement**: Any new logic in `core/` (e.g., a new filter or blending mode) must include a corresponding test.

**Running Tests:**
```
pytest
```


### 5. Pull Request (PR) Process

Code reviews are mandatory. Do not merge your own PR.
1. Open a Pull Request from feature/your-feature into dev.
2. Title: Use the Conventional Commit format (e.g., feat: Add Pencil Tool).
3. Description: Briefly explain what you did and why.
4. Screenshots: If you changed the UI, attach a screenshot.
5. Review: Assign your teammate to review the code.
6. Merge: Once approved, squash and merge into dev.

### 6. Definition of Done

A task is considered "Done" when:
- [ ] The code runs without crashing.
- [ ] It follows the Style Guide (Type hints & Docstrings present).
- [ ] Unit tests pass (if applicable).
- [ ] The PR has been approved by a peer.

Happy Coding! 🎨
