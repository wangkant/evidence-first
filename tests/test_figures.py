"""Exercise real detector findings and the exported figure's provenance/geometry."""
import sys
import tempfile
import unittest
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from pypdf import PdfReader

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/scifig/skills/scifig/scripts"
sys.path.insert(0, str(SCRIPTS))
from figcheck import audit
from figstyle import finalize, panel_labels, save


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

    def test_truncated_horizontal_bar_baseline_is_failure(self):
        fig, ax = plt.subplots()
        ax.barh([0, 1], [10, 11])
        ax.set_xlim(9, 12)
        findings = audit(fig)
        self.assertTrue(any(level == "FAIL" and "bar" in message
                            for level, message in findings))

    def test_log_scale_bars_are_not_reported_as_truncated(self):
        fig, ax = plt.subplots()
        ax.bar([0, 1], [10, 1000])
        ax.set_yscale("log")
        ax.set_xlabel("group")
        ax.set_ylabel("count")
        findings = audit(fig)
        self.assertFalse(any(level == "FAIL" for level, _ in findings), findings)
        self.assertTrue(any("log" in message for _, message in findings), findings)

    def test_panel_labels_skip_colorbar_axes(self):
        for layout in ("constrained", None):
            with self.subTest(layout=layout):
                fig, axes = plt.subplots(1, 2, layout=layout)
                image = axes[1].imshow([[0, 1], [2, 3]])
                fig.colorbar(image, ax=axes[1])
                labels = panel_labels(fig)
                self.assertEqual([t.get_text() for t in labels], ["a", "b"])

    def test_finalize_keeps_constrained_layout_with_colorbar(self):
        fig, ax = plt.subplots(layout="constrained")
        image = ax.imshow([[0, 1], [2, 3]])
        fig.colorbar(image, ax=ax)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            finalize(fig)
        self.assertEqual(type(fig.get_layout_engine()).__name__,
                         "ConstrainedLayoutEngine")

    def test_finalize_names_the_colorbar_when_layout_fails(self):
        fig, ax = plt.subplots()
        image = ax.imshow([[0, 1], [2, 3]])
        fig.colorbar(image, ax=ax)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            finalize(fig)
        messages = [str(w.message) for w in caught]
        if messages:  # older matplotlib may resolve this layout without complaint
            self.assertTrue(any("colorbar" in m for m in messages), messages)

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
