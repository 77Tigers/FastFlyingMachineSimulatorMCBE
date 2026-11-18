/-
Basic data of the FastFlyer simulator (`src/lib.rs`, `src/sim.rs`):
positions, directions, block kinds and blocks, plus the 16-bit cell encoding of
`FORMAT.md` (used only to exchange states with the Rust simulator).

Differences from Rust that cannot matter for any real flyer:
* coordinates are unbounded integers (Rust uses `i64` and treats overflow as an
  error or a failed move).
-/
import Std.Data.ExtTreeMap
import Std.Data.ExtTreeSet

namespace FF

/-- A block position. -/
structure Pos where
  x : Int
  y : Int
  z : Int
  deriving DecidableEq, Repr, Hashable, Inhabited

/-- A world chunk column (16 x 16 in X/Z, after adding the flyer's phase). -/
structure Chunk where
  cx : Int
  cz : Int
  deriving DecidableEq, Repr, Hashable, Inhabited

section Orders
attribute [local instance] lexOrd

def Pos.toTriple (p : Pos) : Int × Int × Int := (p.x, p.y, p.z)
def Chunk.toPair (c : Chunk) : Int × Int := (c.cx, c.cz)

/-- Lexicographic order on (x, y, z), the same as Rust's derived `Ord` for `Coord`. -/
instance : Ord Pos := ⟨compareOn Pos.toTriple⟩
instance : Ord Chunk := ⟨compareOn Chunk.toPair⟩

instance : Std.TransOrd Pos := inferInstanceAs (Std.TransCmp (compareOn Pos.toTriple))
instance : Std.TransOrd Chunk := inferInstanceAs (Std.TransCmp (compareOn Chunk.toPair))

instance : Std.LawfulEqOrd Pos where
  eq_of_compare {a b} h := by
    have : a.toTriple = b.toTriple := Std.LawfulEqOrd.eq_of_compare (α := Int × Int × Int) h
    cases a; cases b; simp_all [Pos.toTriple]

instance : Std.LawfulEqOrd Chunk where
  eq_of_compare {a b} h := by
    have : a.toPair = b.toPair := Std.LawfulEqOrd.eq_of_compare (α := Int × Int) h
    cases a; cases b; simp_all [Chunk.toPair]

end Orders

/-- The six directions, in Rust's order: `+X=0, -X=1, +Y=2, -Y=3, +Z=4, -Z=5`. -/
inductive Dir
  | px | nx | py | ny | pz | nz
  deriving DecidableEq, Repr, Inhabited

namespace Dir

def all : List Dir := [px, nx, py, ny, pz, nz]

def toNat : Dir → Nat
  | px => 0 | nx => 1 | py => 2 | ny => 3 | pz => 4 | nz => 5

def ofNat? : Nat → Option Dir
  | 0 => some px | 1 => some nx | 2 => some py | 3 => some ny | 4 => some pz | 5 => some nz
  | _ => none

def opp : Dir → Dir
  | px => nx | nx => px | py => ny | ny => py | pz => nz | nz => pz

def dx : Dir → Int
  | px => 1 | nx => -1 | _ => 0
def dy : Dir → Int
  | py => 1 | ny => -1 | _ => 0
def dz : Dir → Int
  | pz => 1 | nz => -1 | _ => 0

end Dir

/-- The neighbouring position in direction `d`. -/
def Pos.add (p : Pos) (d : Dir) : Pos := ⟨p.x + d.dx, p.y + d.dy, p.z + d.dz⟩

/-- Block kinds, numbered as in `FORMAT.md`. -/
inductive Kind
  | slime | honey | stone | glass | glazed | redstone | observer | rod | piston | arm
  deriving DecidableEq, Repr, Inhabited

/-- Kinds without direction or state. -/
inductive Plain
  | slime | honey | stone | glass | glazed | redstone | arm
  deriving DecidableEq, Repr, Inhabited

/--
A block. Every constructor carries the `moving` flag (set while a piston's move
of it is unfinished). This type is in bijection with the valid Rust cells.
* `observer d powered moving`: faces `d`; `powered` = a pending output pulse.
* `rod d moving`: an end rod facing `d`.
* `piston d sticky angry state moving`: faces `d`; states 0/1/2/3 =
  retracted / extending / extended / retracting.
-/
inductive Block
  | plain (k : Plain) (moving : Bool)
  | observer (d : Dir) (powered : Bool) (moving : Bool)
  | rod (d : Dir) (moving : Bool)
  | piston (d : Dir) (sticky : Bool) (angry : Bool) (state : Fin 4) (moving : Bool)
  deriving DecidableEq, Repr, Inhabited

def Plain.code : Plain → Nat
  | .slime => 1 | .honey => 2 | .stone => 3 | .glass => 4 | .glazed => 5 | .redstone => 6
  | .arm => 10

namespace Block

def kind : Block → Kind
  | plain .slime _ => .slime
  | plain .honey _ => .honey
  | plain .stone _ => .stone
  | plain .glass _ => .glass
  | plain .glazed _ => .glazed
  | plain .redstone _ => .redstone
  | plain .arm _ => .arm
  | observer .. => .observer
  | rod .. => .rod
  | piston .. => .piston

def moving : Block → Bool
  | plain _ m => m
  | observer _ _ m => m
  | rod _ m => m
  | piston _ _ _ _ m => m

def withMoving (b : Block) (m : Bool) : Block :=
  match b with
  | plain k _ => plain k m
  | observer d p _ => observer d p m
  | rod d _ => rod d m
  | piston d s a st _ => piston d s a st m

def isPiston (b : Block) : Bool := b.kind == .piston

/-- Piston state (0 for every other kind, as Rust's `state()` on a valid cell). -/
def state : Block → Nat
  | piston _ _ _ st _ => st.val
  | _ => 0

/-- Facing (0 = `+X` for kinds without one, as on a valid Rust cell). -/
def dir : Block → Dir
  | observer d _ _ => d
  | rod d _ => d
  | piston d _ _ _ _ => d
  | _ => .px

/-- Rust's `powered()`: only observers carry it. -/
def powered : Block → Bool
  | observer _ p _ => p
  | _ => false

/-! ### Cell encoding (`FORMAT.md`): kind | moving<<4 | dir<<5 | bit8<<8 | angry<<9 | state<<10 -/

def toCell : Block → Nat
  | plain k m => k.code + 16 * m.toNat
  | observer d p m => 7 + 16 * m.toNat + 32 * d.toNat + 256 * p.toNat
  | rod d m => 8 + 16 * m.toNat + 32 * d.toNat
  | piston d s a st m =>
      9 + 16 * m.toNat + 32 * d.toNat + 256 * s.toNat + 512 * a.toNat + 1024 * st.val

/-- Decode a cell exactly as Rust's `Block::from_cell` validates it. -/
def ofCell? (cell : Nat) : Option Block :=
  if cell ≥ 4096 then none else
  let kind := cell % 16
  let m := (cell / 16) % 2 == 1
  let d := (cell / 32) % 8
  let bit8 := (cell / 256) % 2 == 1
  let angry := (cell / 512) % 2 == 1
  let st := (cell / 1024) % 4
  let plainOk := d == 0 && !bit8 && !angry && st == 0
  match kind with
  | 1 => if plainOk then some (plain .slime m) else none
  | 2 => if plainOk then some (plain .honey m) else none
  | 3 => if plainOk then some (plain .stone m) else none
  | 4 => if plainOk then some (plain .glass m) else none
  | 5 => if plainOk then some (plain .glazed m) else none
  | 6 => if plainOk then some (plain .redstone m) else none
  | 10 => if plainOk then some (plain .arm m) else none
  | 7 => if angry || st != 0 then none else (Dir.ofNat? d).map fun d => observer d bit8 m
  | 8 => if bit8 || angry || st != 0 then none else (Dir.ofNat? d).map fun d => rod d m
  | 9 =>
      (Dir.ofNat? d).map fun d =>
        piston d bit8 angry ⟨st, Nat.mod_lt _ (by decide)⟩ m
  | _ => none

end Block

end FF
