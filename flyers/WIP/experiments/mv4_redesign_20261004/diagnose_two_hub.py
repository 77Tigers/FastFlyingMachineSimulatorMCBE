"""Reproduce and record the first balanced-hub interface rejection."""
import json
import runpy
from pathlib import Path

here = Path(__file__).resolve().parent
result_path = here / "two_hubs_results.json"
status_path = here / "two_hubs_status.json"
original_result = json.loads(result_path.read_text())
original_status = status_path.read_text()
survey = runpy.run_path(str(here / "two_hubs.py"))
graph = survey["graph_results"][0]
motif = survey["motifs"][0]
face = survey["cover_sets"][0][0]["assignment"]
config = dict(
    piston_sites=motif["sites"], own=face, previous=face,
    following_ribbons=motif["ribbons"], observers=motif["observers"],
    following=graph["following"], previous_carrier=graph["previous"],
)
_, why = survey["builder"].build(
    0, survey["placements"][graph["placement"]], cap=39,
    joint_router=lambda *args: None, config=config,
)
result = original_result
result["first_failure"]["detail"] = why
result_path.write_text(json.dumps(result, indent=2) + "\n")
status_path.write_text(original_status)
print(json.dumps(result["first_failure"]))
