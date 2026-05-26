"""Smoke tests for STATISTICA pipeline (requires pandas/scipy)."""
import json
import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src_python"))

EXAMPLE = os.path.join(ROOT, "example_dataset.csv")
OUT = os.path.join(ROOT, "output", "_test_smoke")


def require_scientific_stack(testcase):
    missing = [
        package
        for package in ("pandas", "numpy", "scipy")
        if importlib.util.find_spec(package) is None
    ]
    if missing:
        testcase.skipTest("Scientific stack not installed: " + ", ".join(missing))


class TestStatisticaSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(EXAMPLE):
            raise unittest.SkipTest("example_dataset.csv missing")

    def test_diagnostics(self):
        require_scientific_stack(self)
        from diagnostics import run_file_diagnostics

        summary = run_file_diagnostics(EXAMPLE)
        self.assertGreater(summary["rows"], 0)
        self.assertIn("numericColumns", summary)
        self.assertIn("recommendations", summary)

    def test_full_pipeline(self):
        require_scientific_stack(self)
        try:
            from analyzer import execute_automated_analytics
        except ImportError:
            self.skipTest("Scientific stack not installed")

        if os.path.exists(OUT):
            import shutil
            shutil.rmtree(OUT, ignore_errors=True)

        config = {
            "regressionTarget": "Post_Test",
            "regressionPredictors": ["Pre_Test", "Income"],
            "anovaTarget": "Post_Test",
            "anovaGroup": "Group_Factor",
            "exportDpi": 150,
        }
        out_dir = execute_automated_analytics(
            input_path=EXAMPLE,
            custom_output=OUT,
            raw_config=config,
        )
        summary_path = os.path.join(out_dir, "summary.json")
        self.assertTrue(os.path.exists(summary_path))
        with open(summary_path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("linear_regression", data)
        self.assertIn("one_way_anova", data)
        self.assertTrue(os.path.exists(os.path.join(out_dir, "report.html")))


if __name__ == "__main__":
    unittest.main()
