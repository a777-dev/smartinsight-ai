from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.inference import analyze_profile, load_artifacts, load_reference_dataset
from src.insights import generate_insights


class InferenceSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifacts = load_artifacts()
        cls.reference = load_reference_dataset()

    def test_default_profile_produces_expected_keys(self) -> None:
        analysis = analyze_profile({}, self.reference)
        for key in (
            "stress_level",
            "addiction",
            "productivity",
            "behavioral_risk_index",
            "cluster",
            "lifestyle_score",
            "radar",
            "headline",
        ):
            self.assertIn(key, analysis)

    def test_stress_in_range(self) -> None:
        analysis = analyze_profile({"Screen_Time": 11.5, "Sleep_Hours": 4.5}, self.reference)
        self.assertGreaterEqual(analysis["stress_level"], 0.0)
        self.assertLessEqual(analysis["stress_level"], 1.0)

    def test_addiction_label_is_valid(self) -> None:
        analysis = analyze_profile({}, self.reference)
        self.assertIn(analysis["addiction"]["label"], {"Low", "Moderate", "High"})

    def test_insights_are_bounded(self) -> None:
        analysis = analyze_profile({}, self.reference)
        items = generate_insights(
            profile=analysis["profile"],
            stress_norm=analysis["stress_level"],
            productivity_score=analysis["productivity"]["productivity_score"],
            addiction_label=analysis["addiction"]["label"],
            behavioral_risk_index=analysis["behavioral_risk_index"],
            cluster_label=analysis["cluster"]["label"],
        )
        self.assertGreaterEqual(len(items), 1)
        self.assertLessEqual(len(items), 5)


if __name__ == "__main__":
    unittest.main()
