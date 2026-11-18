import Formal.Replay

/-- `replay TRACE...`: check each exported Rust trace against `FF.tick`. -/
def main (args : List String) : IO UInt32 := do
  let mut failures := 0
  for path in args do
    let text ← IO.FS.readFile path
    match FF.Replay.parse text with
    | .error e =>
      IO.println s!"PARSE-ERROR {path}: {e}"
      failures := failures + 1
    | .ok t =>
      match FF.Replay.replay t with
      | .error e =>
        IO.println s!"ERROR {path}: {e}"
        failures := failures + 1
      | .ok (n, none) => IO.println s!"OK {path}: {n} ticks"
      | .ok (n, some msg) =>
        IO.println s!"MISMATCH {path}: {n} ticks matched; {msg}"
        failures := failures + 1
  return if failures == 0 then 0 else 1
