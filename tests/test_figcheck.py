"""Regression tests using real image files and the public command line."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pypdf import PdfWriter

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/scifig/skills/scifig/scripts"
sys.path.insert(0, str(SCRIPTS))
from figcheck import check_file


class FileChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def raster(self, name="figure.png", dpi=(300, 300)):
        path = self.root / name
        Image.new("RGB", (600, 300), "white").save(path, dpi=dpi)
        return path

    def cli(self, path, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "figcheck.py"),
                               str(path), *args], capture_output=True, text=True)

    def test_jpeg_failure_reaches_shell(self):
        result = self.cli(self.raster("figure.jpg"))
        self.assertIn("[FAIL]", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_warning_is_nonblocking_by_default(self):
        result = self.cli(self.raster(dpi=(72, 72)))
        self.assertIn("[WARN]", result.stdout)
        self.assertEqual(result.returncode, 0)

    def test_strict_mode_fails_on_warning(self):
        result = self.cli(self.raster(dpi=(72, 72)), "--strict")
        self.assertIn("[WARN]", result.stdout)
        self.assertEqual(result.returncode, 1)

    def test_high_resolution_png_passes_strict(self):
        result = self.cli(self.raster(), "--strict", "--inches", "2", "1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_input_is_failure(self):
        issues = check_file(str(self.root / "absent.png"))
        self.assertTrue(any(level == "FAIL" for level, _ in issues))

    def test_unknown_format_does_not_claim_pass(self):
        path = self.root / "figure.txt"
        path.write_text("not a figure")
        result = self.cli(path, "--strict")
        self.assertIn("unsupported", result.stdout.lower())
        self.assertEqual(result.returncode, 1)

    def test_corrupt_input_is_reported_without_traceback(self):
        path = self.root / "broken.png"
        path.write_bytes(b"not a PNG")
        result = self.cli(path)
        self.assertIn("[FAIL]", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.returncode, 1)

    def test_raster_height_mismatch_is_detected(self):
        issues = check_file(str(self.raster()), expect_inches=(2, 2))
        self.assertTrue(any(level == "WARN" and "height" in msg for level, msg in issues))

    def test_vertical_dpi_is_checked(self):
        issues = check_file(str(self.raster(dpi=(300, 72))))
        self.assertTrue(any(level == "WARN" and "dpi" in msg for level, msg in issues))

    def test_pdf_height_mismatch_is_detected(self):
        path = self.root / "figure.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=144, height=72)
        with path.open("wb") as stream:
            writer.write(stream)
        issues = check_file(str(path), expect_inches=(2, 2))
        self.assertTrue(any(level == "WARN" and "height" in msg for level, msg in issues))

    def test_pdf_missing_page_geometry_is_failure(self):
        path = self.root / "broken.pdf"
        writer = PdfWriter()
        page = writer.add_blank_page(width=144, height=72)
        del page["/MediaBox"]
        with path.open("wb") as stream:
            writer.write(stream)
        result = self.cli(path)
        self.assertIn("[FAIL]", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.returncode, 1)

    def test_invalid_dimensions_are_usage_error(self):
        result = self.cli(self.raster(), "--inches", "nan", "2")
        self.assertEqual(result.returncode, 2)

    def test_invalid_dpi_threshold_is_usage_error(self):
        result = self.cli(self.raster(), "--min-dpi", "0")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
