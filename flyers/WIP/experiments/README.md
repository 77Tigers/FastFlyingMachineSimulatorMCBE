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

For new work, start with the short [`INDEX.md`](INDEX.md) and update its active lead pointers. Use the runner's compact CSV output for screens and samples; keep full traces in the owned experiment directory and quote only the first relevant failure in chat.

Before reporting a result, maintain your experiment's `FINDINGS.md`, the active [`INDEX.md`](INDEX.md), and the central [`RESEARCH_LOG.md`](../../RESEARCH_LOG.md) as needed. Record what passed, what failed, the tested bounds, the best file and evidence paths, and the next causal question. If you change the research runner, update [`RESEARCH_RUNNER.md`](RESEARCH_RUNNER.md) in the same turn. The agent doing the work owns these updates.
