"""n3_09: C:-|S:mmmww|push@2|T:mmmww  (loose piston B53 pushes B54; B49,B51 removed)."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parent))
from _n3lib import *

SRC = "flyers/bank/pl12/human_3bps_original.flyer"
T0 = 100


def spec(R):
    return dict(id="n3_09", src=SRC, t0=T0, keep=["B53", "B40", "B54"], recurrence="exact",
                ports=[dict(name="b40_carrier_in", role="input", ident=pick(R, "B40", "sl", 0), prescribe=[2, 3, 4]),
                       dict(name="b54_in", role="input", ident=pick(R, "B54", "sl", 1), prescribe=[0, 1]),
                       dict(name="b54_out", role="output", ident=pick(R, "B54", "sl", 0))])

if __name__ == "__main__":
    run(sys.modules[__name__], D, samples=True)
