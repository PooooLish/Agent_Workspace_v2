# Git First Commit SOP

Use this SOP before creating the first workspace commit or any later broad structural commit.

## Procedure

1. Run `python capabilities/tools/check_workspace.py`.
2. Run `python capabilities/tools/audit_git_readiness.py`.
3. Run `python capabilities/tools/summarize_git_candidates.py`.
4. Run `python capabilities/tools/prepare_first_commit_report.py`.
5. Review `runtime/outputs/first_commit_recommendation.md`.
6. Confirm that generated outputs, logs, dependency folders, raw media, and local secrets are ignored.
7. Confirm that concrete task folders are ignored and `git ls-files tasks` only shows intended public placeholders.
8. Stage only the intended baseline files.
9. Run the checks again after staging if the staged set is broad.

## Safety rules

- Do not stage real secrets, credentials, private keys, or local `.env` files.
- Do not stage dependency folders such as `node_modules/`.
- Do not stage raw media, generated renders, logs, caches, or temporary files unless explicitly intended.
- Do not stage local backup files such as `*.bak`; keep the canonical file instead.
- Concrete task files must not be staged in the workspace root repository. Publish an approved task only through an independent Git repository initialized inside that task directory.
- Do not delete cleanup candidates without explicit approval.

## Expected report

End with:

- candidate file count
- readiness audit result
- baseline recommendation path
- notable large files, if any
- files or directories intentionally excluded
- remaining private task or cleanup items
