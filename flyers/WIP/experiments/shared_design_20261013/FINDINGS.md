# Search-integration findings

The source-to-contract gap is closed for named contact geometry, movement
provenance and required initial cells. Standalone Python contracts enforce the
same compiled assertions as the design CLI. The Rust search evaluator enforces
those assertions too, and required coordinates are immutable during mutation.

Evidence is in README.md and integration/: 81 Python tests, 2 Rust assertion
tests, 26 migration differential checks, 25 positive legacy comparisons,
400 migrated sample cases per evaluator. Three migrated seed files are
byte-identical to the published originals; generated views reproduce unchanged.
The n2_04 after-natural failure remains separately labelled and reproduced.

These checks cover the preserved reference-derived scenarios and deliberately
broken assertions. They do not establish complete evaluator equivalence or
universal update-order safety. Rust retains its stricter extension-failure rule
and existing search defaults; use explicit order/recurrence for comparisons.

Required initial cells preserve selected material/state contents, not rigid-body
membership at every intermediate phase. Internal provenance names a natural
movement, not a particular actuator, action kind or power provider. Those richer
obligations and fresh-agent construction trials are the remaining abstraction
work. No new flyer push limit was achieved in this integration.
