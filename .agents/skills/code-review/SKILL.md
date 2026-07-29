---
name: code-review
description: Use when the user asks to review a patch, branch, pull request, or local diff for correctness, regressions, risky assumptions, maintainability issues, and missing tests.
---

# Code Review

## Purpose

Review code changes for bugs, regressions, risky assumptions, and missing tests.

## When to use

Use when a patch, branch, or local diff needs a quality and risk review.

## Procedure

1. Read the relevant files and understand intent.
2. Identify correctness, safety, and maintainability issues.
3. Check whether tests cover the changed behavior.
4. Report findings in severity order with file references.

## Safety rules

- Do not approve behavior you did not verify.
- Prefer concrete findings over vague style feedback.
- Flag missing test coverage when it creates risk.

## Expected output

A concise review with prioritized findings, assumptions, and suggested next steps.
