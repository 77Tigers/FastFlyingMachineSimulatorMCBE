import unittest

from tools.extension_route import RouteError, check_route


def template():
    return {
        "version": 1,
        "name": "route-test",
        "target_word": "wwmmm",
        "contacts": [[0, 0, 0], [2, 0, 0]],
        "blockers": [],
        "reserved": [],
        "glue_budget": 3,
    }


class ExtensionRouteTests(unittest.TestCase):
    def test_no_obstacles_returns_manhattan_shortest_path(self):
        result = check_route(template())
        self.assertEqual(result["verdict"], "within_budget")
        self.assertEqual(result["required_glue"], 3)
        self.assertTrue(result["required_glue_exact"])
        self.assertEqual(len(result["path"]), 3)

    def test_blockers_force_a_detour(self):
        request = template()
        request["contacts"] = [[0, 0, 0], [2, 0, 0]]
        request["blockers"] = [{"word": "wwmmm", "cells": [[1, 0, 0]]}]
        request["glue_budget"] = 5
        result = check_route(request)
        self.assertEqual(result["verdict"], "within_budget")
        self.assertEqual(result["required_glue"], 5)
        self.assertNotIn([1, 0, 0], result["path"])

    def test_budget_exclusion_then_optional_path_finds_diagonal_witness(self):
        request = {
            "version": 1, "name": "diagonal-route-bound", "target_word": "wwmmm",
            "contacts": [[3, 0, 0], [-1, 1, 1]],
            "blockers": [{"word": "mmmww", "cells": [[0, 0, 0], [0, 1, 1], [0, 1, 0]]}],
            "reserved": [[2, 0, 1]], "glue_budget": 8,
        }
        rejected = check_route(request)
        self.assertEqual(rejected["verdict"], "over_budget")
        self.assertEqual(rejected["required_glue"], 9)
        self.assertFalse(rejected["required_glue_exact"])
        self.assertIsNone(rejected["path"])
        found = check_route(request, search_depth=9)
        self.assertEqual(found["verdict"], "over_budget")
        self.assertEqual(found["required_glue"], 9)
        self.assertTrue(found["required_glue_exact"])
        self.assertEqual(found["path"][0], [3, 0, 0])
        self.assertEqual(found["path"][-1], [-1, 1, 1])
        self.assertEqual(len(found["path"]), 9)
        for a, b in zip(found["path"], found["path"][1:]):
            self.assertEqual(sum(abs(a[i] - b[i]) for i in range(3)), 1)

    def test_invalid_words_and_contact_overlap_are_rejected(self):
        request = template()
        request["target_word"] = "wwmxm"
        with self.assertRaises(RouteError):
            check_route(request)
        request = template()
        request["blockers"] = [{"word": "mmwww", "cells": [[0, 0, 0]]}]
        with self.assertRaises(RouteError):
            check_route(request)
        request = template()
        request["reserved"] = [[0, 0, 0]]
        with self.assertRaises(RouteError):
            check_route(request)
        request = template()
        request["blockers"] = [{"word": "wwmmm", "cells": [[0, 0, 0]]}]
        with self.assertRaises(RouteError):
            check_route(request)

    def test_node_cap_is_unknown_not_a_negative_proof(self):
        request = template()
        request["contacts"] = [[0, 0, 0], [100, 100, 100]]
        request["glue_budget"] = 5
        result = check_route(request, max_nodes=1)
        self.assertEqual(result["verdict"], "unknown")
        self.assertEqual(result["search"]["status"], "node_cap_before_budget_proof")
        self.assertIsNone(result["required_glue"])
        self.assertFalse(result["required_glue_exact"])

    def test_depth_limited_route_search_keeps_only_the_proven_budget_bound(self):
        request = template()
        request["contacts"] = [[0, 0, 0], [100, 100, 100]]
        request["glue_budget"] = 3
        result = check_route(request, search_depth=6)
        self.assertEqual(result["verdict"], "over_budget")
        self.assertEqual(result["required_glue"], 4)
        self.assertIsNone(result["path"])
        self.assertEqual(result["search"]["status"], "budget_excluded_no_path_to_depth_limit")

    def test_optional_node_cap_does_not_erase_completed_budget_proof(self):
        request = template()
        request["contacts"] = [[0, 0, 0], [100, 100, 100]]
        request["glue_budget"] = 5
        result = check_route(request, search_depth=10, max_nodes=200)
        self.assertEqual(result["verdict"], "over_budget")
        self.assertEqual(result["required_glue"], 6)
        self.assertEqual(result["search"]["status"], "budget_excluded_optional_search_capped")


if __name__ == "__main__":
    unittest.main()
