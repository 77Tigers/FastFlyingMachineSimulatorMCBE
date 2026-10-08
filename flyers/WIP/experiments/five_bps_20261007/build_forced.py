"""Build a TEMP-only forced-chunk-order diagnostic library, never production sim."""
from pathlib import Path
import tempfile,subprocess
root=Path.cwd();out=Path(tempfile.gettempdir())/'fastflyer-5bps-proof';out.mkdir(exist_ok=True)
for name in ['lib.rs','sim.rs','debug.rs']:(out/name).write_bytes((root/'src'/name).read_bytes())
p=out/'sim.rs';s=p.read_text();s=s.replace('        shuffle(&mut chunks, tick_seed);','''        shuffle(&mut chunks, tick_seed);
        // Diagnostic override: G = completing bank first, B = starting bank first.
        static STEP: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
        let t = STEP.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        if let Ok(word) = std::env::var("ORDER_WORD") {
            let good = word.as_bytes()[t % word.len()] == b'G';
            let first_z = if (t % 2 == 0) == good { 1 } else { 0 };
            chunks.sort_by_key(|c| (if c.1 == first_z { 0 } else { 1 }, c.0));
        }
''');p.write_text(s)
subprocess.run(['rustc','--edition=2021','--crate-name','fastflyer','--crate-type','rlib','-O',str(out/'lib.rs'),'-o',str(out/'libfastflyer.rlib')],check=True)
print(out)
