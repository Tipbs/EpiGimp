# **CI/CD GitHub Actions**

EpiGimp relies on a single multi-OS pipeline described in .github/workflows/build-shared.yml. It guarantees that the application remains installable, buildable, and packageable on both Linux and Windows environments upon every change.

## **Triggers**

* push on any branch.  
* pull\_request on any branch.

## **Jobs**

### **build — Cross-platform Build & Package**

**Strategy:** Matrix execution on ubuntu-latest and windows-latest.  
**Fail-fast:** false (A failure on Windows does not cancel the Linux build, allowing independent debugging).

1. **Checkout**: Retrieves the repository source code (actions/checkout@v4).  
2. **System Dependencies (Linux only)**: Installs required shared libraries (libglib2.0-0, libgl1, libgomp1) necessary for OpenCV and PySide6 headless rendering.  
3. **Python Setup**: Initializes Python 3.10 (actions/setup-python@v4).  
4. **Dependency Installation**:  
   * Upgrades pip.  
   * Installs project requirements via requirements.txt.  
   * Installs the project in editable mode (pip install \-e .).  
5. **Packaging**:  
   * Installs pyinstaller.  
   * Builds the standalone executable using main.spec.  
6. **Artifact Upload**: Uploads the binary generated in dist/ as a workflow artifact:  
   * EpiGimp-Linux (binary)  
   * EpiGimp-Windows (.exe)  
7. **Tests**: *Currently disabled* (configured with if: false).

The two matrix jobs run in parallel. No external secrets are required; the default permissions are sufficient for artifact uploads.

## **Good Practices & Evolution**

* **Enable Tests**: Remove the if: false condition in the final step to actively run pytest before packaging.  
* **Caching**: Implement actions/cache for pip dependencies to reduce build time (approx. 1-2 minutes saved per run).  
* **Linting Step**: Add a dedicated step for flake8 or black before the build to fail early on style violations.  
* **Release Trigger**: Limit the PyInstaller packaging step to tag pushes or the main branch to save CI minutes on feature branches.  
* **Artifact Retention**: Configure a retention period (e.g., 5 days) for build artifacts to manage storage limits.
