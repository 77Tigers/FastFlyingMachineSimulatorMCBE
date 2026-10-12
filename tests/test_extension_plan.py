import unittest

from tools.extension_plan import PlanError, _world_position, check_plan


def plan_template():
    return {
        "version": 1,
        "name": "five-slot-contact",
        "slot_ticks": 2,
        "period_slots": 5,
        "advance": 2,
        "objects": [
            {"name": "front", "at": [0, 4, 0], "word": "mmwww"},
            {"name": "follower", "at": [2, 4, 0], "word": "wwwmm"},
        ],
        "contacts": [
            {"name": "approach", "a": "front", "b": "follower", "slots": [1], "relation": "adjacent"},
            {"name": "initial-clearance", "a": "front", "b": "follower", "slots": [0], "relation": "adjacent", "required": False},
        ],
    }


class ExtensionPlanTests(unittest.TestCase):
    def test_five_slot_movement_can_create_and_release_contact(self):
        plan = plan_template()
        plan["contacts"].append({
            "name": "release",
            "a": "front",
            "b": "follower",
            "slots": [2],
            "relation": "adjacent",
            "required": False,
        })
        result = check_plan(plan)
        self.assertEqual(result["verdict"], "consistent")
        self.assertIn("power, states, connectivity", result["message"])

    def test_forbidden_static_contact_is_contradicted(self):
        plan = plan_template()
        plan["objects"][0]["word"] = "wwmwm"
        plan["objects"][1]["word"] = "wwmwm"
        plan["objects"][1]["at"] = [1, 4, 0]
        plan["contacts"] = [{
            "name": "must-separate",
            "a": "front",
            "b": "follower",
            "slots": [0],
            "relation": "adjacent",
            "required": False,
        }]
        result = check_plan(plan)
        self.assertEqual(result["verdict"], "contradicted")
        self.assertEqual(result["mismatch"]["world_positions"], {"front": [0, 4, 0], "follower": [1, 4, 0]})
        self.assertEqual(result["mismatch"]["actual_vector_b_minus_a"], [1, 0, 0])
        self.assertEqual(result["mismatch"]["tick"], 0)

    def test_next_cycle_starts_after_declared_advance(self):
        plan = plan_template()
        front = {"at": tuple(plan["objects"][0]["at"]), "word": plan["objects"][0]["word"]}
        self.assertEqual(_world_position(front, 0, advance=2, cycle=1), (2, 4, 0))

    def test_rejects_malformed_plan_fields_and_types(self):
        plan = plan_template()
        plan["extra"] = True
        with self.assertRaises(PlanError):
            check_plan(plan)

        plan = plan_template()
        plan["objects"][0]["at"] = [False, 4, 0]
        with self.assertRaises(PlanError):
            check_plan(plan)

        plan = plan_template()
        plan["contacts"][0]["slots"] = []
        with self.assertRaises(PlanError):
            check_plan(plan)

        plan = plan_template()
        plan["objects"][1]["word"] = "wwwww"
        with self.assertRaises(PlanError):
            check_plan(plan)


if __name__ == "__main__":
    unittest.main()
