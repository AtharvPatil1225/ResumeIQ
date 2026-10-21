"""
test_predict_match.py
---------------------
Tests for predict_match.py.

These tests verify the module's behaviour without requiring a real
trained model file.  The import-time crash bug is tested by importing
the module and confirming it does not raise on import.
"""

import pytest
from predict_match import predict_match, load_model


class TestImportDoesNotCrash:
    """Importing predict_match must not raise FileNotFoundError."""

    def test_module_imports_cleanly(self):
        # The module-level import must not crash even if no model exists.
        import predict_match  # noqa: F401


class TestLoadModelRaisesWhenMissing:
    def test_load_model_raises_file_not_found(self, tmp_path):
        missing = tmp_path / "nonexistent_model.joblib"
        with pytest.raises(FileNotFoundError, match="Trained model not found"):
            load_model(model_path=missing)


class TestPredictMatchValidation:
    def test_empty_resume_raises_value_error(self):
        with pytest.raises(ValueError, match="resume_text"):
            predict_match("", "Python developer with SQL experience.")

    def test_whitespace_resume_raises_value_error(self):
        with pytest.raises(ValueError, match="resume_text"):
            predict_match("   ", "Python developer required.")

    def test_empty_job_description_raises_value_error(self):
        with pytest.raises(ValueError, match="job_description"):
            predict_match("Python developer with SQL.", "")

    def test_whitespace_job_description_raises_value_error(self):
        with pytest.raises(ValueError, match="job_description"):
            predict_match("Python developer.", "   ")
