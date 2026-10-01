"""setlimit.py SRC LIMIT OUT : copy a flyer with a different encoded push limit (RNG/phase unchanged)."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from fastflyer import Flyer
src,limit,out=sys.argv[1:4]
f=Flyer.load(src); f.push_limit=int(limit); f.save(out); print(out,'limit',limit)
