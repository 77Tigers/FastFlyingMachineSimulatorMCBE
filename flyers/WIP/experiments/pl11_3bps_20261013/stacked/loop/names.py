import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "extract"))
import xlib as X
SRC = 'flyers/bank/pl12/human_3bps_original.flyer'
M = X.Model(SRC, 100)
def idnames(D, keep_names=None):
    """fixture identity (initial coord) -> body name, rebuilt from candidate coords via the same translation as build_plan."""
    import xlib
    D = Path(D).resolve()
    f = X.Flyer.load(D / "candidate.flyer")
    # find translation: match body cells of any kept body by trying delta from min coordinates
    return f
