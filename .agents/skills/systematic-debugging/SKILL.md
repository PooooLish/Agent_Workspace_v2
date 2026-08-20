---
name: systematic-debugging
description: Use when a bug, failing test, crash, timeout, flaky behavior, performance regression, or unexplained system behavior must be diagnosed before changing implementation code.
---

# Systematic Debugging

## Core principle

Find the cause before changing the code. A plausible workaround is not evidence.

## Workflow

1. **Reproduce and bound the failure.** Capture the exact command, inputs,
   environment, frequency, expected behavior, actual behavior, and first bad
   boundary. If reproduction is intermittent, collect multiple failing and
   passing samples.
2. **Read the evidence.** Inspect complete errors, logs, stack traces, recent
   changes, and component boundaries. Trace bad values or state backward to
   their origin instead of patching the final symptom.
3. **Form one falsifiable hypothesis.** State the suspected cause, the evidence
   supporting it, and one observation that would disprove it.
4. **Test one variable.** Use the smallest diagnostic experiment. Do not combine
   cleanup, refactoring, dependency upgrades, or multiple speculative fixes.
5. **Create a regression test.** Make the original failure observable and verify
   that the test fails for the expected reason.
6. **Implement the smallest causal fix.** Run the focused regression, relevant
   neighboring tests, and any required workspace checks.
7. **Report evidence and uncertainty.** Distinguish confirmed cause, mitigation,
   unresolved hypothesis, and verified fix.

## Evidence record

Keep a compact record while investigating:

| Field | Required content |
| --- | --- |
| Symptom | Exact failure and affected boundary |
| Reproduction | Command, inputs, environment, frequency |
| Evidence | Logs, trace, diff, measurements |
| Hypothesis | Cause plus disconfirming observation |
| Experiment | One changed variable and result |
| Verification | Regression and neighboring checks |

## Example

For an intermittent CI timeout, compare successful and failing logs, identify
the unmet wait condition, and instrument that boundary. Raising the timeout is
only a labeled mitigation unless evidence proves the operation merely needs
more time; it is not a root-cause fix.

## Stop conditions

Stop proposing code changes when:

- the failure has not been reproduced or bounded;
- the hypothesis cannot be falsified;
- the experiment changes more than one causal variable;
- the proposed fix only hides an error, retry, race, timeout, or warning;
- three attempted fixes failed without producing new evidence.

After three failed fixes, return to the architecture and assumptions. Do not
stack another speculative change.

## Common rationalizations

| Excuse | Reality |
| --- | --- |
| "The workaround is harmless." | Unexplained changes create hidden failure modes. |
| "There is no time to reproduce." | State the blocker; do not relabel a guess as a fix. |
| "Several fixes together are faster." | Combined changes destroy causal evidence. |
| "The test is flaky anyway." | Flakiness is a symptom requiring evidence, not dismissal. |
