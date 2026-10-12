"""Reconstruct the prescribed one-period boundary and track K0's piston passenger."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
trace_path = HERE / "two_input_before_trace.ndjson"
rows = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines() if line]
base = {tuple(block[:3]): block[3] for block in rows[0]["trace"]["initial"]}
last = rows[7]["trace"]
final = {tuple(block[:3]): block[3] for block in last["initial"]}
for step in last["steps"]:
    for x, y, z, encoded in step.get("changes", []):
        pos = (x, y, z)
        if encoded is None:
            final.pop(pos, None)
        else:
            final[pos] = encoded
shifted = {(x - 2, y, z): encoded for (x, y, z), encoded in final.items()}
diffs = []
for pos in sorted(base.keys() | shifted.keys()):
    if base.get(pos) != shifted.get(pos):
        diffs.append({"normalized_at": list(pos), "initial_encoded": base.get(pos),
                      "final_shifted_encoded": shifted.get(pos)})

chain = [{"tick": 0, "actor": [2, 1, 15], "cause": "N sticky pulls K0",
          "source": [0, 1, 17], "destination": [1, 1, 17]},
         {"tick": 2, "actor": [3, 1, 16], "cause": "K1 sticky pulls K0+N",
          "source": [1, 1, 17], "destination": [2, 1, 17]},
         {"tick": 4, "actor": "prescribed K1 input", "cause": "K1 +X input",
          "source": [2, 1, 17], "destination": [3, 1, 17]},
         {"tick": 6, "actor": "prescribed K1 input", "cause": "K1 +X input",
          "source": [3, 1, 17], "destination": [4, 1, 17]}]
for event in chain:
    tick = event["tick"]
    steps = rows[tick]["trace"]["steps"]
    source = event["source"]
    assert any(source in (step.get("movement") or {}).get("sources", []) for step in steps), (tick, source)
assert diffs == [
    {"normalized_at": [0, 1, 17], "initial_encoded": 9, "final_shifted_encoded": None},
    {"normalized_at": [2, 1, 17], "initial_encoded": None, "final_shifted_encoded": 9},
]
initial_owners = rows[0]["trace"]["initial_owners"]
final_owners = last["steps"][-1].get("owners", [])
result = {"period_ticks": 8, "advance": 2, "initial_cell_count": len(base),
          "final_cell_count": len(final), "shifted_final_cell_count": len(shifted),
          "cell_differences": diffs, "initial_owners": initial_owners,
          "final_owners": final_owners, "owner_difference": [],
          "original_identity_chain": chain,
          "tick8_actor": {"identity_origin": [0, 1, 17],
                          "actual_at": [4, 1, 17],
                          "action_sources": [[4, 0, 17], [5, 0, 16], [5, 0, 17],
                                             [5, 1, 16], [5, 1, 17]]}}
(HERE / "boundary_diff.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
