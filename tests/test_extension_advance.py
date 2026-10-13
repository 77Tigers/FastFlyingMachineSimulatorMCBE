"""Tests for the per-identity advance recurrence mode."""

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from extension_contract import CaseChecker, Contract, Port


def make_checker(initial, *, recurrence="advance", envelope=None):
    return CaseChecker(
        Contract("advance-test", Path("fixture.flyer"), 2, 1, 1,
                 (Port("out", "output", tuple(initial[0][0:3]), "m", None, None),),
                 recurrence, envelope),
        {"initial": initial, "initial_owners": [], "steps": []})


class ExtensionAdvanceTests(unittest.TestCase):
    def test_advance_rejects_stationary_junk(self):
        checker = make_checker([[0, 0, 0, 1], [0, 0, 1, 1]])
        checker.ids[0] = (1, 0, 0)
        checker.cells = {(1, 0, 0): 1, (0, 0, 1): 1}

        failure = checker.check_boundary(1)

        self.assertIn("permanent identity 1", failure)
        self.assertIn("expected (1, 0, 1)", failure)

    def test_advance_accepts_changed_piston_state_without_state_recurrence(self):
        checker = make_checker([[0, 0, 0, 9], [0, 0, 1, 9]])
        checker.ids = {0: (1, 0, 0), 1: (1, 0, 1)}
        checker.cells = {(1, 0, 0): 25, (1, 0, 1): 9}
        checker.owners = (((1, 0, 0), (2, 2, 3)),)

        self.assertIsNone(checker.check_boundary(1))

    def test_advance_rejects_permutation_of_identity_destinations(self):
        checker = make_checker([[0, 0, 0, 1], [2, 0, 0, 1]])
        checker.ids = {0: (3, 0, 0), 1: (1, 0, 0)}
        checker.cells = {(3, 0, 0): 1, (1, 0, 0): 1}

        failure = checker.check_boundary(1)

        self.assertIn("permanent identity 0", failure)
        self.assertIn("expected (1, 0, 0)", failure)

    def test_exact_mode_still_requires_translated_cells_and_owners(self):
        checker = make_checker([[0, 0, 0, 1]], recurrence="exact")
        checker.ids[0] = (1, 0, 0)
        checker.cells = {(1, 0, 0): 1}

        self.assertIsNone(checker.check_boundary(1))
        checker.cells[(1, 0, 0)] = 17
        self.assertIn("recurrence mismatch", checker.check_boundary(1))

    def test_bounded_mode_still_uses_translated_envelope(self):
        checker = make_checker([[0, 0, 0, 1]], recurrence="bounded",
                               envelope=((0, 0, 0), (1, 0, 0)))
        checker.ids[0] = (1, 0, 0)

        self.assertIsNone(checker.check_boundary(1))
        checker.ids[0] = (0, 0, 0)
        self.assertIn("outside translated boundary_envelope", checker.check_boundary(1))


if __name__ == "__main__":
    unittest.main()
