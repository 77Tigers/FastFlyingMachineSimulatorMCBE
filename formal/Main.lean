import Formal.Replay

/-- `replay TRACE...`: check each exported Rust trace against `FF.tick`.
`replay --wf TRACE...`: report whether each trace's start state satisfies `Wf` (diagnostic). -/
def main (args : List String) : IO UInt32 := do
  if args.head? == some "--wf" then
    for path in args.tail do
      let text ← IO.FS.readFile path
      match FF.Replay.parse text with
      | .error e => IO.println s!"PARSE-ERROR {path}: {e}"
      | .ok t =>
        match FF.Replay.stateOf t.blocks t.lists with
        | .error e => IO.println s!"ERROR {path}: {e}"
        | .ok s =>
          match FF.Replay.wfViolation t.config s with
          | none => IO.println s!"WF {path}"
          | some v => IO.println s!"NOT-WF {path}: {v}"
    return 0
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
