"""Exercise real detector findings and the exported figure's provenance/geometry."""
import sys
import tempfile
import unittest
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from pypdf import PdfReader

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/scifig/skills/scifig/scripts"
sys.path.insert(0, str(SCRIPTS))
from figcheck import audit
from figstyle import save


class FigureChecks(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_truncated_bar_baseline_is_failure(self):
        fig, ax = plt.subplots()
        ax.bar([0, 1], [10, 11])
        ax.set_ylim(9, 12)
        findings = audit(fig)
        self.assertTrue(any(level == "FAIL" and "bar" in message
                            for level, message in findings))

    def test_rainbow_mapping_is_failure(self):
        fig, ax = plt.subplots()
        ax.imshow([[0, 1], [2, 3]], cmap="jet")
        findings = audit(fig)
        self.assertTrue(any(level == "FAIL" and "rainbow" in message
                            for level, message in findings))

    def test_export_preserves_geometry_and_source(self):
        fig, ax = plt.subplots(figsize=(3, 2))
        ax.plot([0, 1], [1, 2])
        with tempfile.TemporaryDirectory() as tmp:
            paths = save(fig, str(Path(tmp) / "figure"), dpi=300,
                         provenance={"data": "fixture.csv"})
            self.assertEqual(len(paths), 2)
            pdf = PdfReader(paths[0])
            self.assertAlmostEqual(float(pdf.pages[0].mediabox.width) / 72, 3)
            self.assertAlmostEqual(float(pdf.pages[0].mediabox.height) / 72, 2)
            self.assertIn("fixture.csv", pdf.metadata.subject)
            with Image.open(paths[1]) as png:
                self.assertEqual(png.size, (900, 600))
                self.assertIn("fixture.csv", png.info["Description"])


if __name__ == "__main__":
    unittest.main()
