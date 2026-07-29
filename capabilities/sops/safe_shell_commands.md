# Safe Shell Commands SOP

Commands that require manual confirmation before running:

1. File deletion commands such as `rm`, `del`, `Remove-Item`, or recursive cleanup.
2. Move or sync commands that can overwrite data, such as `mv`, `Move-Item`, `rsync`, or `robocopy` into existing targets.
3. History-rewriting git commands such as `git reset`, `git clean`, `git checkout --`, or force push.
4. Network install commands such as `curl | sh`, `wget | sh`, `pip install`, `conda install`, or package-manager upgrades.
5. Permission-changing commands such as `sudo`, `chmod -R`, or ownership changes.
6. Broad find-and-replace commands across many files.
