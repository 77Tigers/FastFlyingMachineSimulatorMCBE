# Research workspace

Keep the existing candidates, logs, and results. They record both successful
designs and failed searches; a short-lived or interrupted experiment is not
evidence that the search is exhausted. The active handoff is
[`../../RESEARCH_LOG.md`](../../RESEARCH_LOG.md), with earlier work linked there.

For new experiments, keep the generator or diagnostic source next to a short
finding note. Record parameters, encoded push limit, RNG seed, X/Z phases,
tick budget, distance, conservation result, and the first failure. Keep a
representative `.flyer` and compact CSV/JSON results for each useful outcome.
Mark diagnostic high-limit runs distinctly from verified bank entries. The
current research files have not been pruned or reclassified.

Generated `.flyer` candidates remain ignored by Git. Once a result meets the
verification contract in the active handoff, copy the verified encoded-limit
file into [`../../bank/`](../../bank/) and add its `results.csv` row. Banked
`.flyer` files are eligible for version control.

Original compiled tools are retained locally in the ignored `bin/archive/`,
with their former subdirectory structure. New builds go into the ignored
`bin/` output area. [`BINARY_RELOCATION.csv`](BINARY_RELOCATION.csv)
records every moved binary's original path, new path, size, and SHA-256 hash.
Source files and research evidence remain in their original locations. Build
the portable runner with [`build_research_runner.ps1`](build_research_runner.ps1);
its usage is in [`RESEARCH_RUNNER.md`](RESEARCH_RUNNER.md).
