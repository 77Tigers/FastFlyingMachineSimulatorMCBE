"""Run finite sweep categories in bounded, resumable chunks."""
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent
for category in sys.argv[1:]:
    while True:
        trial=subprocess.run([sys.executable,str(HERE/'sweeps.py'),category,'1200'])
        if trial.returncode==0:break
        if trial.returncode!=3:sys.exit(trial.returncode)
