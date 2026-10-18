"""
conftest.py
-----------
Shared pytest configuration for ResumeIQ.
Ensures src/ is on sys.path for all test files.
"""

import sys
from pathlib import Path

# Insert src/ at the front of sys.path so that all test modules
# can import project packages without any manual PYTHONPATH setup.
_SRC_DIR = str(Path(__file__).resolve().parent / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
