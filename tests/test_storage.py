import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from fastflyer import Block, Flyer, FormatError, Kind


class StorageTests(unittest.TestCase):
    def make_flyer(self):
        flyer = Flyer(phase_x=7, phase_z=11, rng_state=42, push_limit=12)
        flyer.set((-17, -3, 0), Block.piston(0, sticky=True, angry=True, state=3, moving=True))
        flyer.set((18, -3, 0), Block.piston(5, moving=True))
        flyer.set((-16, -2, 0), Block(Kind.PISTON_ARM, moving=True))
        flyer.set_piston_blocks((-17, -3, 0), [(-16, -2, 0)])
        flyer.set_piston_blocks((18, -3, 0), [(-16, -2, 0)])
        return flyer

    def test_round_trip_preserves_all_requested_fields(self):
        flyer = self.make_flyer()
        original = flyer.blocks()
        raw = flyer.to_bytes()
        self.assertEqual(flyer.blocks(), original)  # saving does not move editor coordinates
        loaded = Flyer.from_bytes(raw)
        self.assertEqual(raw, loaded.to_bytes())
        self.assertEqual((loaded.phase_x, loaded.phase_z, loaded.rng_state, loaded.push_limit),
                         (7, 11, 42, 12))
        self.assertEqual(loaded.get((15, 0, 0)),
                         Block.piston(0, sticky=True, angry=True, state=3, moving=True))
        self.assertEqual(loaded.get((16, 1, 0)), Block(Kind.PISTON_ARM, moving=True))
        self.assertEqual(loaded.get_piston_blocks((15, 0, 0)), ((16, 1, 0),))
        self.assertEqual(loaded.get_piston_blocks((50, 0, 0)), ((16, 1, 0),))

    def test_moving_bit_on_every_kind(self):
        flyer = Flyer()
        for x, kind in enumerate(Kind):
            if kind == Kind.AIR:
                continue
            if kind == Kind.OBSERVER:
                block = Block.observer(2, powered=True, moving=True)
            elif kind == Kind.ROD:
                block = Block.rod(3, moving=True)
            elif kind == Kind.PISTON:
                block = Block.piston(4, moving=True)
            else:
                block = Block(kind, moving=True)
            flyer.set((x, 0, 0), block)
        loaded = Flyer.from_bytes(flyer.to_bytes())
        self.assertTrue(all(block.moving for _, block in loaded.blocks()))
        self.assertEqual(loaded.occupied_count(), 10)

    def test_boundaries_and_rng_continuation(self):
        flyer = Flyer(phase_x=15, phase_z=0)
        positions = [(-17, -17, -17), (-16, -16, -16), (-1, -1, -1),
                     (0, 0, 0), (15, 15, 15), (16, 16, 16), (31, 31, 31)]
        for pos in positions:
            flyer.set(pos, Block(Kind.HONEY, moving=True))
        self.assertEqual(flyer.next_random_u64(), 0xE220A8397B1DCDAF)
        loaded = Flyer.from_bytes(flyer.to_bytes())
        self.assertEqual(flyer.next_random_u64(), loaded.next_random_u64())
        self.assertEqual(loaded.occupied_count(), len(positions))
        self.assertEqual(loaded.to_bytes(), flyer.to_bytes())

    def test_editing_and_call_counts(self):
        flyer = Flyer()
        flyer.fill_box((-1, 0, -1), (1, 0, 1), Block(Kind.GLASS))
        self.assertEqual(flyer.operation_counts()["successful"]["fill_box"], 1)
        self.assertNotIn("set", flyer.operation_counts()["successful"])
        flyer.rotate_y()
        flyer.mirror("z")
        self.assertEqual(flyer.occupied_count(), 9)
        with self.assertRaises(ValueError):
            flyer.fill_line((0, 0, 0), (1, 1, 0), Block(Kind.SLIME))
        self.assertEqual(flyer.operation_counts()["failed"]["fill_line"], 1)

    def test_python_and_rust_write_identical_files(self):
        if shutil.which("cargo") is None:
            self.skipTest("Rust toolchain unavailable")
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source.flyer"
            rewritten = Path(temp) / "rewritten.flyer"
            flyer = self.make_flyer()
            flyer.set((-1, -16, -17), Block.observer(4, powered=True, moving=True))
            flyer.set((16, 16, 16), Block.rod(2, moving=True))
            flyer.save(source)
            subprocess.run(["cargo", "run", "--quiet", "--example", "roundtrip", "--",
                            str(source), str(rewritten)], check=True,
                           cwd=Path(__file__).resolve().parents[1], capture_output=True)
            self.assertEqual(source.read_bytes(), rewritten.read_bytes())

    def test_reject_bad_cell(self):
        flyer = Flyer()
        flyer.set((0, 0, 0), Block(Kind.SLIME))
        raw = bytearray(flyer.to_bytes())
        raw[-3] = 0  # preserve index, change low cell byte to air
        raw[-2] = 0
        with self.assertRaises(FormatError):
            Flyer.from_bytes(raw)

    def test_rotation_updates_direction_and_piston_references(self):
        flyer = Flyer()
        flyer.set((1, 0, 0), Block.piston(0, moving=True))
        flyer.set_piston_blocks((1, 0, 0), [(2, 0, 0)])
        flyer.rotate_y()
        self.assertEqual(flyer.get((0, 0, 1)), Block.piston(4, moving=True))
        self.assertEqual(flyer.get_piston_blocks((0, 0, 1)), ((0, 0, 2),))
        flyer.mirror("z")
        self.assertEqual(flyer.get((0, 0, -1)), Block.piston(5, moving=True))


if __name__ == "__main__":
    unittest.main()
