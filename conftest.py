"""Pytest configuration for gui_designer tests."""

import sys
import pytest

# Skip entire session if PyQt6 is not available.
# Import the marker early so collection doesn't fail.
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_pyqt6: mark test as requiring PyQt6"
    )


@pytest.fixture(scope="session")
def qapp():
    """Create a single QApplication instance shared across all tests."""
    PyQt6 = pytest.importorskip("PyQt6")
    from PyQt6.QtWidgets import QApplication

    existing = QApplication.instance()
    if existing is not None:
        yield existing
    else:
        app = QApplication(sys.argv[:1])
        yield app
        # Do not call app.quit() here to avoid interfering with other tests.