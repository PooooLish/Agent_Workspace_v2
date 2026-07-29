# Line Endings SOP

Use this SOP when `python -B capabilities/tools/audit_line_endings.py` reports drift from `.gitattributes`.

## Procedure

1. Run `python -B capabilities/tools/audit_line_endings.py --examples 20`.
2. Separate root/workspace files from task-specific files.
3. Normalize files only inside the current task scope unless a broader cleanup was explicitly requested.
4. After any normalization, run `python -B capabilities/tools/audit_line_endings.py` again.
5. Run `python -B capabilities/tools/run_workspace_maintenance.py` before handoff.

## Safety Rules

- Do not rewrite unrelated task files just to reduce the reminder count.
- Do not normalize binary files.
- Do not combine line ending cleanup with behavior changes.
- Keep PowerShell, batch, and command scripts compatible with the `.gitattributes` CRLF policy.
- Keep Markdown, Python, JSON, YAML, CSS, HTML, shell, and web source files compatible with the `.gitattributes` LF policy.

## Strict Mode

Use strict mode only after the known drift is intentionally reduced:

```powershell
python -B capabilities/tools/audit_line_endings.py --strict
```

Strict mode returns nonzero when any drift remains.

## Expected Report

End with:

- line ending drift count before changes
- files normalized, if any
- line ending drift count after changes
- whether strict mode was used
