---
name: cli-tool-setup
description: Use when a task depends on an existing command-line tool and needs safe local setup notes, command examples, prerequisites, or verification steps; do not use when building a new CLI.
---

# CLI Tool Setup

## Purpose

Document or prepare a safe workflow for command-line tools used in a task.

## When to use

Use when a task depends on a CLI and the user needs local usage notes or templates.

## Procedure

1. Identify the tool and the task-specific commands.
2. Write usage notes, examples, and verification steps.
3. Keep tool-specific details inside task docs or shared env notes.
4. Record any manual prerequisites instead of auto-installing them.

## Safety rules

- Do not run unknown install scripts.
- Do not edit global config without approval.
- Ask before any destructive command.

## Expected output

A short setup guide or task-specific CLI usage note that is safe to follow.
