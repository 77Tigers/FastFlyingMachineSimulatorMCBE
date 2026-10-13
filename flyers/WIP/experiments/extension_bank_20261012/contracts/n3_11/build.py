"""n3_11: C:wwmmm|S:-|pull@1|T:mmwmw  (pl14 mmwmw_two_pulls: B37 sticky pulls B20; B37/B42/B30 mutual cluster)."""
import sys
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parent))
from _n3lib import *

SRC = "flyers/bank/pl14/mmwmw_two_pulls.flyer"
T0 = 100


def spec(R):
    return dict(id="n3_11", src=SRC, t0=T0, recurrence="bounded",
                keep=["B37", "B20", "B30", "B42", "B28", "B29", "B32", "B39", "B40", "B41"],
                ports=[dict(name="b20_in", role="input", ident=pick(R, "B20", "sl", 0), prescribe=[0]),
                       dict(name="b30_in", role="input", ident=pick(R, "B30", "ho", 0), prescribe=[0, 4]),
                       dict(name="b20_out", role="output", ident=pick(R, "B20", "sl", 1)),
                       dict(name="b30_out", role="output", ident=pick(R, "B30", "ho", 1)),
                       dict(name="b37_out", role="output", ident=pick(R, "B37", "sl", 0)),
                       dict(name="b42_out", role="output", ident=pick(R, "B42", "sl", 0))])

if __name__ == "__main__":
    run(sys.modules[__name__], D, samples=True)
