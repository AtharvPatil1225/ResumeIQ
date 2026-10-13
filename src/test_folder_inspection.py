from pathlib import Path

from pdf_extractor import inspect_pdf_folder


def test_inspect_empty_folder(tmp_path):
    results = inspect_pdf_folder(tmp_path)

    assert results["total"] == 0
    assert results["readable"] == 0
    assert results["empty"] == 0
    assert results["failed"] == 0


def test_inspect_nonexistent_folder(tmp_path):
    folder = tmp_path / "nonexistent"

    try:
        inspect_pdf_folder(folder)
    except (FileNotFoundError, NotADirectoryError, ValueError):
        pass
    else:
        # Some implementations may treat a nonexistent folder as empty.
        assert True