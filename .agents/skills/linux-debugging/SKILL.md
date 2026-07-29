---
name: linux-debugging
description: Use when debugging Linux-specific commands, processes, filesystems, permissions, containers, shells, environment variables, or behavior that differs from Windows.
---

# Linux Debugging

## Purpose

Debug Linux-side command, process, filesystem, or environment problems in a structured way.

## When to use

Use when behavior differs across shells, servers, containers, or Linux environments.

## Procedure

1. Capture the exact error and command.
2. Reproduce with the smallest possible steps.
3. Inspect logs, exit codes, paths, and environment variables.
4. Change one factor at a time.
5. Re-run the minimum verification command.

## Safety rules

- Do not assume root access.
- Do not delete logs before reading them.
- Avoid broad cleanup commands without confirmation.

## Expected output

A minimal reproduction, likely cause, fix, and verification result.
