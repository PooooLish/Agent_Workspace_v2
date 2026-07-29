# Git And Task Isolation

V2 is independent from the source workspace. It neither copies task assets nor
uses links or junctions to expose them.

The external task root is declared in `.workspace/config.json` with
`access: read_only`. Tools may show task state, but mutating task commands must
call the centralized permission guard before loading or executing task content.

Source-protection baselines are stored under
`runtime/runs/source-baseline/`. They record root Git state, task path and file
hash inventories, nested repository state, and volatile-file paths. Any
difference between before and after baselines requires investigation; tools must
not repair the source automatically.

V2 Git audits must run with V2 as their working directory. Nested repositories
under the external task root are separate repositories and remain outside V2
maintenance scope.
