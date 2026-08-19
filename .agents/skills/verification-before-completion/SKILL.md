---
name: verification-before-completion
description: Use when preparing to claim that code, a fix, a build, tests, a migration, or a task is complete, correct, passing, or ready to commit, push, merge, release, or hand off.
---

# Verification Before Completion

## Core principle

Make claims from fresh evidence, not confidence or earlier results.

```
NO COMPLETION CLAIM WITHOUT CURRENT VERIFICATION EVIDENCE
```

## Verification gate

Before any completion, success, readiness, commit, push, merge, or release
claim:

1. **Define the claim.** State exactly what is supposedly correct or ready.
2. **Choose proof.** Map the claim to the command or inspection that can prove
   it. A test does not prove a build; a lint run does not prove behavior.
3. **Run it now.** Execute the complete relevant command after the final change.
4. **Read the result.** Check exit code, failures, warnings, skipped work, and
   whether the command covered the claimed scope.
5. **Report proportionally.** State the command, result, coverage, and any
   unverified limitation. If proof failed or could not run, report that status
   instead of completion.

## Evidence contract

Every completion report contains:

| Field | Content |
| --- | --- |
| Claim | The exact behavior or artifact asserted ready |
| Evidence | Fresh command or direct inspection |
| Result | Exit code and meaningful pass/fail counts |
| Scope | What the evidence covered |
| Limits | Anything skipped, unavailable, or still uncertain |

## Examples

- "`python -m pytest tests/test_api.py` passed 18 tests after the final edit;
  the browser flow was not exercised."
- "The build has not been verified because dependencies are unavailable; the
  source change is implemented but not ready to release."

## Invalid substitutes

These do not support a completion claim:

- a test run from before the final change;
- a partial command presented as full coverage;
- another Agent's success report without independent confirmation;
- a diff that looks correct;
- "should pass", "likely fixed", or CI that has not finished;
- hiding warnings, skipped tests, or a nonzero exit behind a positive summary.

## Common rationalizations

| Excuse | Reality |
| --- | --- |
| "It was only a one-line change." | One line can invalidate earlier evidence. |
| "CI will catch it later." | Pending CI is not current proof. |
| "The focused test passed." | Limit the claim to the focused behavior. |
| "The tool failed for an unrelated reason." | Report the blocker and the unverified state. |

If the final verification changes files or state, inspect that change and run
the relevant gate again before claiming completion.
