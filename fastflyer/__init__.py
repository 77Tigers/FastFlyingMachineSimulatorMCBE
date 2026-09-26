"""Editing and version-1 disk storage for Bedrock flying machines."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from enum import IntEnum
from functools import wraps
from hashlib import sha256
import json
from pathlib import Path
import struct
from typing import Callable, Iterable, Iterator

Coord = tuple[int, int, int]
MAGIC = b"FFLY"
VERSION = 1
U64_MAX = (1 << 64) - 1
I64_MAX = (1 << 63) - 1


class FormatError(ValueError):
    """A flyer file is malformed or uses unsupported data."""


class Kind(IntEnum):
    AIR = 0
    SLIME = 1
    HONEY = 2
    SMOOTH_STONE = 3
    GLASS = 4
    GLAZED_TERRACOTTA = 5
    REDSTONE_BLOCK = 6
    OBSERVER = 7
    ROD = 8
    PISTON = 9
    PISTON_ARM = 10


DIRECTIONS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


@dataclass(frozen=True, slots=True)
class Block:
    kind: Kind
    moving: bool = False
    direction: int = 0
    powered: bool = False
    sticky: bool = False
    angry: bool = False
    state: int = 0

    def __post_init__(self) -> None:
        kind = Kind(self.kind)
        object.__setattr__(self, "kind", kind)
        if any(type(value) is not bool for value in
               (self.moving, self.powered, self.sticky, self.angry)):
            raise ValueError("moving, powered, sticky, and angry must be booleans")
        if type(self.direction) is not int or type(self.state) is not int:
            raise ValueError("direction and state must be integers")
        if kind == Kind.AIR:
            raise ValueError("air is represented by an absent cell")
        if not 0 <= self.direction <= 5:
            raise ValueError("direction must be 0..5")
        if not 0 <= self.state <= 3:
            raise ValueError("piston state must be 0..3")
        if kind not in (Kind.OBSERVER, Kind.ROD, Kind.PISTON) and self.direction:
            raise ValueError("this block has no direction")
        if kind != Kind.OBSERVER and self.powered:
            raise ValueError("only observers have powered state")
        if kind != Kind.PISTON and (self.sticky or self.angry or self.state):
            raise ValueError("only pistons have sticky, angry, or state fields")

    @classmethod
    def observer(cls, direction: int, powered: bool = False, moving: bool = False) -> Block:
        return cls(Kind.OBSERVER, moving=moving, direction=direction, powered=powered)

    @classmethod
    def rod(cls, direction: int, moving: bool = False) -> Block:
        return cls(Kind.ROD, moving=moving, direction=direction)

    @classmethod
    def piston(cls, direction: int, sticky: bool = False, angry: bool = False,
               state: int = 0, moving: bool = False) -> Block:
        return cls(Kind.PISTON, moving=moving, direction=direction,
                   sticky=sticky, angry=angry, state=state)

    def encode(self) -> int:
        cell = int(self.kind) | (int(self.moving) << 4)
        cell |= self.direction << 5
        if self.kind == Kind.OBSERVER:
            cell |= int(self.powered) << 8
        if self.kind == Kind.PISTON:
            cell |= int(self.sticky) << 8
            cell |= int(self.angry) << 9
            cell |= self.state << 10
        return cell

    @classmethod
    def decode(cls, cell: int) -> Block:
        try:
            kind = Kind(cell & 15)
        except ValueError as exc:
            raise FormatError(f"unknown block kind: {cell & 15}") from exc
        if kind == Kind.AIR or cell & 0xF000:
            raise FormatError("air record or nonzero reserved cell bits")
        moving = bool(cell & 16)
        direction = (cell >> 5) & 7
        bit8 = bool(cell & 256)
        angry = bool(cell & 512)
        state = (cell >> 10) & 3
        try:
            if kind == Kind.OBSERVER:
                if angry or state:
                    raise FormatError("observer has unsupported state bits")
                return cls.observer(direction, bit8, moving)
            if kind == Kind.ROD:
                if bit8 or angry or state:
                    raise FormatError("rod has unsupported state bits")
                return cls.rod(direction, moving)
            if kind == Kind.PISTON:
                return cls.piston(direction, bit8, angry, state, moving)
            if direction or bit8 or angry or state:
                raise FormatError("plain block has unsupported state bits")
            return cls(kind, moving=moving)
        except ValueError as exc:
            raise FormatError(str(exc)) from exc


def _coord(value: Iterable[int]) -> Coord:
    parts = tuple(value)
    if len(parts) != 3 or any(type(v) is not int for v in parts):
        raise ValueError("coordinate must contain three integers")
    return parts  # type: ignore[return-value]


def _counted(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self: Flyer, *args, **kwargs):
        outer = self._call_depth == 0
        self._call_depth += 1
        try:
            result = method(self, *args, **kwargs)
        except Exception:
            if outer:
                self._failed_calls[method.__name__] += 1
            raise
        else:
            if outer:
                self._successful_calls[method.__name__] += 1
            return result
        finally:
            self._call_depth -= 1
    return wrapper


class Flyer:
    """Mutable sparse editor. Negative coordinates are valid until serialization."""

    def __init__(self, phase_x: int = 0, phase_z: int = 0,
                 rng_state: int = 0, push_limit: int = 12):
        if any(type(value) is not int for value in
               (phase_x, phase_z, rng_state, push_limit)):
            raise ValueError("phases, RNG state, and push limit must be integers")
        if not 0 <= phase_x < 16 or not 0 <= phase_z < 16:
            raise ValueError("X/Z phases must be 0..15")
        if not 0 <= rng_state <= U64_MAX:
            raise ValueError("RNG state must be a u64")
        if not 0 <= push_limit <= U64_MAX:
            raise ValueError("push limit must be a nonnegative u64")
        self.phase_x = phase_x
        self.phase_z = phase_z
        self.rng_state = rng_state
        self.push_limit = push_limit
        self._cells: dict[Coord, Block] = {}
        self._piston_blocks: dict[Coord, tuple[Coord, ...]] = {}
        self._successful_calls: Counter[str] = Counter()
        self._failed_calls: Counter[str] = Counter()
        self._call_depth = 0

    @_counted
    def next_random_u64(self) -> int:
        """Advance the stored SplitMix64 state and return its next output."""
        mask = U64_MAX
        self.rng_state = (self.rng_state + 0x9E3779B97F4A7C15) & mask
        value = self.rng_state
        value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & mask
        value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & mask
        return value ^ (value >> 31)

    @_counted
    def set(self, pos: Coord, block: Block) -> None:
        pos = _coord(pos)
        if not isinstance(block, Block):
            raise TypeError("block must be a Block")
        self._cells[pos] = block
        if block.kind != Kind.PISTON:
            self._piston_blocks.pop(pos, None)

    @_counted
    def get(self, pos: Coord) -> Block | None:
        return self._cells.get(_coord(pos))

    @_counted
    def remove(self, pos: Coord) -> Block | None:
        pos = _coord(pos)
        self._piston_blocks.pop(pos, None)
        return self._cells.pop(pos, None)

    @_counted
    def set_piston_blocks(self, piston: Coord, blocks: Iterable[Coord]) -> None:
        piston = _coord(piston)
        if self._cells.get(piston, None) is None or self._cells[piston].kind != Kind.PISTON:
            raise ValueError("owner coordinate must contain a piston")
        members = tuple(_coord(pos) for pos in blocks)
        if len(members) > self.push_limit:
            raise ValueError("piston list exceeds push limit")
        if len(set(members)) != len(members):
            raise ValueError("piston list contains duplicate coordinates")
        if members:
            self._piston_blocks[piston] = tuple(sorted(members))
        else:
            self._piston_blocks.pop(piston, None)

    @_counted
    def get_piston_blocks(self, piston: Coord) -> tuple[Coord, ...]:
        return self._piston_blocks.get(_coord(piston), ())

    @_counted
    def fill_box(self, start: Coord, end: Coord, block: Block) -> None:
        a, b = _coord(start), _coord(end)
        if not isinstance(block, Block):
            raise TypeError("block must be a Block")
        for x in range(min(a[0], b[0]), max(a[0], b[0]) + 1):
            for y in range(min(a[1], b[1]), max(a[1], b[1]) + 1):
                for z in range(min(a[2], b[2]), max(a[2], b[2]) + 1):
                    self.set((x, y, z), block)

    @_counted
    def clear_region(self, start: Coord, end: Coord) -> int:
        a, b = _coord(start), _coord(end)
        selected = [pos for pos in self._cells if all(
            min(a[i], b[i]) <= pos[i] <= max(a[i], b[i]) for i in range(3))]
        for pos in selected:
            self.remove(pos)
        return len(selected)

    @_counted
    def replace(self, pos: Coord, old: Block | None, new: Block | None) -> bool:
        pos = _coord(pos)
        if self._cells.get(pos) != old:
            return False
        if new is None:
            self.remove(pos)
        else:
            self.set(pos, new)
        return True

    @_counted
    def blocks(self) -> list[tuple[Coord, Block]]:
        return sorted(self._cells.items())

    @_counted
    def blocks_of_type(self, kind: Kind) -> list[tuple[Coord, Block]]:
        kind = Kind(kind)
        return [(pos, block) for pos, block in sorted(self._cells.items()) if block.kind == kind]

    @_counted
    def neighbors(self, pos: Coord) -> list[tuple[Coord, Block]]:
        x, y, z = _coord(pos)
        result = []
        for dx, dy, dz in DIRECTIONS:
            neighbor = (x + dx, y + dy, z + dz)
            if neighbor in self._cells:
                result.append((neighbor, self._cells[neighbor]))
        return result

    @_counted
    def bounds(self) -> tuple[Coord, Coord] | None:
        if not self._cells:
            return None
        positions = self._cells
        return (tuple(min(pos[i] for pos in positions) for i in range(3)),
                tuple(max(pos[i] for pos in positions) for i in range(3)))  # type: ignore[return-value]

    @_counted
    def occupied_count(self) -> int:
        return len(self._cells)

    @_counted
    def translate(self, dx: int, dy: int, dz: int) -> None:
        delta = _coord((dx, dy, dz))
        shift = lambda p: tuple(p[i] + delta[i] for i in range(3))
        self._cells = {shift(pos): block for pos, block in self._cells.items()}
        self._piston_blocks = {shift(pos): tuple(shift(p) for p in blocks)
                               for pos, blocks in self._piston_blocks.items()}

    def _transform(self, point: Callable[[Coord], Coord],
                   direction: Callable[[int], int]) -> None:
        transformed = {}
        for pos, block in self._cells.items():
            if block.kind in (Kind.OBSERVER, Kind.ROD, Kind.PISTON):
                block = replace(block, direction=direction(block.direction))
            transformed[point(pos)] = block
        self._cells = transformed
        self._piston_blocks = {point(pos): tuple(sorted(point(p) for p in blocks))
                               for pos, blocks in self._piston_blocks.items()}

    @_counted
    def rotate_y(self, quarter_turns: int = 1) -> None:
        """Rotate about (0,0,0); one turn sends +X to +Z."""
        if type(quarter_turns) is not int:
            raise ValueError("quarter_turns must be an integer")
        turns = quarter_turns % 4
        direction_map = (4, 5, 2, 3, 1, 0)
        for _ in range(turns):
            self._transform(lambda p: (-p[2], p[1], p[0]),
                            lambda d: direction_map[d])

    @_counted
    def mirror(self, axis: str) -> None:
        """Reflect coordinates and facing across the named coordinate axis."""
        if axis not in ("x", "y", "z"):
            raise ValueError("axis must be x, y, or z")
        index = "xyz".index(axis)
        flipped = (1, 0, 3, 2, 5, 4)
        def point(p: Coord) -> Coord:
            values = list(p)
            values[index] = -values[index]
            return tuple(values)  # type: ignore[return-value]
        def direction(d: int) -> int:
            return flipped[d] if d // 2 == index else d
        self._transform(point, direction)

    @_counted
    def copy_region(self, start: Coord, end: Coord) -> Flyer:
        a, b = _coord(start), _coord(end)
        result = Flyer(self.phase_x, self.phase_z, self.rng_state, self.push_limit)
        result._cells = {pos: block for pos, block in self._cells.items() if all(
            min(a[i], b[i]) <= pos[i] <= max(a[i], b[i]) for i in range(3))}
        result._piston_blocks = {pos: members for pos, members in self._piston_blocks.items()
                                 if pos in result._cells}
        return result

    @_counted
    def paste(self, other: Flyer, offset: Coord = (0, 0, 0),
              overwrite: bool = True) -> None:
        if not isinstance(other, Flyer):
            raise TypeError("other must be a Flyer")
        dx, dy, dz = _coord(offset)
        def shift(pos: Coord) -> Coord:
            return pos[0] + dx, pos[1] + dy, pos[2] + dz
        if not overwrite and any(shift(pos) in self._cells for pos in other._cells):
            raise ValueError("paste would overwrite existing blocks")
        if any(len(members) > self.push_limit for members in other._piston_blocks.values()):
            raise ValueError("pasted piston list exceeds destination push limit")
        # Snapshot first so pasting a flyer into itself works.
        cells = [(shift(pos), block) for pos, block in other._cells.items()]
        extras = [(shift(pos), tuple(shift(p) for p in members))
                  for pos, members in other._piston_blocks.items()]
        for pos, block in cells:
            self.set(pos, block)
        for pos, members in extras:
            self.set_piston_blocks(pos, members)

    @_counted
    def diff(self, other: Flyer) -> dict[str, list[Coord]]:
        if not isinstance(other, Flyer):
            raise TypeError("other must be a Flyer")
        before, after = set(self._cells), set(other._cells)
        common = before & after
        changed = {pos for pos in common if self._cells[pos] != other._cells[pos]
                   or self._piston_blocks.get(pos, ()) != other._piston_blocks.get(pos, ())}
        return {"added": sorted(after - before), "removed": sorted(before - after),
                "changed": sorted(changed)}

    def _normalized(self) -> tuple[dict[Coord, Block], dict[Coord, tuple[Coord, ...]]]:
        coords = list(self._cells)
        for owner, members in self._piston_blocks.items():
            coords.append(owner)
            coords.extend(members)
        if not coords:
            return {}, {}
        mins = [min(pos[i] for pos in coords) for i in range(3)]
        shifts = (-(mins[0] // 16) * 16, -mins[1], -(mins[2] // 16) * 16)
        def move(pos: Coord) -> Coord:
            result = tuple(pos[i] + shifts[i] for i in range(3))
            if any(v < 0 or v > I64_MAX for v in result):
                raise ValueError("normalized coordinate exceeds shared Rust coordinate range")
            return result  # type: ignore[return-value]
        cells = {move(pos): block for pos, block in self._cells.items()}
        extras = {move(pos): tuple(sorted(move(member) for member in members))
                  for pos, members in self._piston_blocks.items()}
        return cells, extras

    @_counted
    def canonicalize(self) -> Flyer:
        cells, extras = self._normalized()
        flyer = Flyer(self.phase_x, self.phase_z, self.rng_state, self.push_limit)
        flyer._cells, flyer._piston_blocks = cells, extras
        return flyer

    @_counted
    def validate(self) -> list[str]:
        problems = []
        for owner, members in self._piston_blocks.items():
            if owner not in self._cells or self._cells[owner].kind != Kind.PISTON:
                problems.append(f"{owner}: piston list has no piston owner")
            if len(members) > self.push_limit:
                problems.append(f"{owner}: piston list exceeds push limit")
            if len(set(members)) != len(members):
                problems.append(f"{owner}: piston list has duplicates")
        return problems

    @_counted
    def iter_sections(self) -> list[tuple[Coord, list[tuple[Coord, Block]]]]:
        sections: dict[Coord, list[tuple[Coord, Block]]] = {}
        for pos, block in self._cells.items():
            key = (pos[0] // 16, pos[1] // 16, pos[2] // 16)
            sections.setdefault(key, []).append((pos, block))
        return [(key, sorted(sections[key])) for key in sorted(sections)]

    @_counted
    def iter_chunk_columns(self) -> list[tuple[tuple[int, int], list[tuple[Coord, Block]]]]:
        columns: dict[tuple[int, int], list[tuple[Coord, Block]]] = {}
        for pos, block in self._cells.items():
            key = (pos[0] // 16, pos[2] // 16)
            columns.setdefault(key, []).append((pos, block))
        return [(key, sorted(columns[key])) for key in sorted(columns)]

    @_counted
    def to_bytes(self) -> bytes:
        problems = self.validate()
        if problems:
            raise ValueError("; ".join(problems))
        cells, extras = self._normalized()
        sections: dict[tuple[int, int, int], list[tuple[int, int]]] = {}
        for (x, y, z), block in cells.items():
            key = (x // 16, z // 16, y // 16)
            index = ((y & 15) << 8) | ((z & 15) << 4) | (x & 15)
            sections.setdefault(key, []).append((index, block.encode()))
        data = bytearray(MAGIC)
        data.extend(struct.pack("<HBBQ", VERSION, self.phase_x, self.phase_z, self.rng_state))
        data.extend(_varint(self.push_limit))
        data.extend(_varint(len(sections)))
        for key in sorted(sections):
            for number in key:
                data.extend(_varint(number))
            records = sorted(sections[key])
            data.extend(_varint(len(records)))
            for index, cell in records:
                data.extend(struct.pack("<HH", index, cell))
        data.extend(_varint(len(extras)))
        for owner in sorted(extras):
            for number in owner:
                data.extend(_varint(number))
            members = extras[owner]
            data.extend(_varint(len(members)))
            for pos in members:
                for number in pos:
                    data.extend(_varint(number))
        return bytes(data)

    @classmethod
    def from_bytes(cls, raw: bytes) -> Flyer:
        reader = _Reader(raw)
        if reader.take(4) != MAGIC:
            raise FormatError("invalid magic")
        version, phase_x, phase_z, rng_state = struct.unpack("<HBBQ", reader.take(12))
        if version != VERSION:
            raise FormatError(f"unsupported version {version}")
        try:
            flyer = cls(phase_x, phase_z, rng_state, reader.varint())
        except ValueError as exc:
            raise FormatError(str(exc)) from exc
        section_count = reader.varint()
        previous_key = None
        for _ in range(section_count):
            cx, cz, sy = reader.varint(), reader.varint(), reader.varint()
            key = (cx, cz, sy)
            if previous_key is not None and key <= previous_key:
                raise FormatError("subchunks are not strictly sorted")
            previous_key = key
            count = reader.varint()
            if not 1 <= count <= 4096:
                raise FormatError("invalid occupied count")
            previous_index = -1
            for _ in range(count):
                index, cell = struct.unpack("<HH", reader.take(4))
                if index >= 4096 or index <= previous_index:
                    raise FormatError("invalid or unsorted local index")
                previous_index = index
                pos = (cx * 16 + (index & 15), sy * 16 + (index >> 8),
                       cz * 16 + ((index >> 4) & 15))
                flyer._cells[pos] = Block.decode(cell)
        list_count = reader.varint()
        previous_owner = None
        for _ in range(list_count):
            owner = (reader.varint(), reader.varint(), reader.varint())
            if previous_owner is not None and owner <= previous_owner:
                raise FormatError("piston lists are not strictly sorted")
            previous_owner = owner
            count = reader.varint()
            if not 1 <= count <= flyer.push_limit:
                raise FormatError("invalid piston list length")
            members = []
            previous_member = None
            for _ in range(count):
                member = (reader.varint(), reader.varint(), reader.varint())
                if previous_member is not None and member <= previous_member:
                    raise FormatError("piston members are not strictly sorted")
                previous_member = member
                members.append(member)
            if flyer._cells.get(owner, None) is None or flyer._cells[owner].kind != Kind.PISTON:
                raise FormatError("piston list owner has no piston")
            flyer._piston_blocks[owner] = tuple(members)
        if reader.remaining():
            raise FormatError("trailing bytes")
        flyer._successful_calls["load"] += 1
        return flyer

    @_counted
    def save(self, path: str | Path) -> None:
        Path(path).write_bytes(self.to_bytes())

    @classmethod
    def load(cls, path: str | Path) -> Flyer:
        return cls.from_bytes(Path(path).read_bytes())

    @_counted
    def content_hash(self) -> str:
        return sha256(self.to_bytes()).hexdigest()

    @_counted
    def to_json(self, indent: int | None = 2) -> str:
        """Human-readable view of the current editor coordinates and state."""
        data = {
            "format_version": VERSION,
            "phase_x": self.phase_x,
            "phase_z": self.phase_z,
            "rng_state": self.rng_state,
            "push_limit": self.push_limit,
            "blocks": [
                {"position": pos, "kind": block.kind.name.lower(),
                 "moving": block.moving, "direction": block.direction,
                 "powered": block.powered, "sticky": block.sticky,
                 "angry": block.angry, "state": block.state}
                for pos, block in sorted(self._cells.items())
            ],
            "piston_lists": [
                {"piston": owner, "blocks": members}
                for owner, members in sorted(self._piston_blocks.items())
            ],
        }
        return json.dumps(data, indent=indent)

    def operation_counts(self) -> dict[str, dict[str, int]]:
        return {"successful": dict(self._successful_calls),
                "failed": dict(self._failed_calls)}


def _varint(value: int) -> bytes:
    if not 0 <= value <= U64_MAX:
        raise ValueError("unsigned variable integer is outside u64 range")
    data = bytearray()
    while value >= 128:
        data.append((value & 127) | 128)
        value >>= 7
    data.append(value)
    return bytes(data)


class _Reader:
    def __init__(self, raw: bytes):
        self.raw = raw
        self.offset = 0

    def take(self, length: int) -> bytes:
        end = self.offset + length
        if end > len(self.raw):
            raise FormatError("truncated file")
        chunk = self.raw[self.offset:end]
        self.offset = end
        return chunk

    def varint(self) -> int:
        value = 0
        for index in range(10):
            byte = self.take(1)[0]
            if index == 9 and byte > 1:
                raise FormatError("variable integer exceeds u64")
            value |= (byte & 127) << (7 * index)
            if not byte & 128:
                if index and byte == 0:
                    raise FormatError("overlong variable integer")
                return value
        raise FormatError("overlong variable integer")

    def remaining(self) -> int:
        return len(self.raw) - self.offset


__all__ = ["Block", "Coord", "DIRECTIONS", "Flyer", "FormatError", "Kind"]
