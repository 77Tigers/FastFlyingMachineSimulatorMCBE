"""n3_10: C:mwwmm|S:-|pull@2|T:mmmww  (B40 sticky piston retracts and pulls B23 + riders; B40<->B23 joint ring cell)."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parent))
from _n3lib import *

SRC = "flyers/bank/pl12/human_3bps_original.flyer"
T0 = 100


def spec(R):
    return dict(id="n3_10", src=SRC, t0=T0, keep=["B40", "B23", "B26", "B27", "B30", "B54", "B49", "B51", "B53"], recurrence="bounded",
                ports=[dict(name="b23_in", role="input", ident=pick(R, "B23", "sl", 0), prescribe=[0, 4]),
                       dict(name="b23_out", role="output", ident=pick(R, "B23", "sl", 1)),
                       dict(name="b40_out", role="output", ident=pick(R, "B40", "sl", 0)),
                       dict(name="b54_out", role="output", ident=pick(R, "B54", "sl", 0))])

if __name__ == "__main__":
    run(sys.modules[__name__], D, samples=True)
