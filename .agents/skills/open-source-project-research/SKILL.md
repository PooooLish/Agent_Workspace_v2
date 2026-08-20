---
name: open-source-project-research
description: Use when starting a software project, choosing an implementation approach, or deciding whether to reference, integrate, adapt, or fork open-source repositories.
---

# Open Source Project Research

## Overview

Research current open-source options before implementation. Make the choice,
evidence, license obligations, and permitted reuse boundary traceable without
turning a small project into a long review cycle.

## Workflow

1. Define the problem, required capabilities, constraints, target stack, and
   search date.
2. Search the web and relevant source hosts. Prefer primary evidence: repository
   README, license file, releases, security policy or advisories, issue activity,
   commits, and official documentation.
3. Shortlist three to five viable candidates when available. If fewer qualify,
   record what was searched and why.
4. Compare each candidate on:
   - exact source URL and reviewed version, tag, or commit;
   - license, notices, attribution, redistribution, and copyleft obligations;
   - maintenance activity, release cadence, issue health, and project maturity;
   - known advisories, dependency risk, security policy, and unsafe defaults;
   - technical fit, architecture quality, tests, documentation, and integration
     cost;
   - proposed reuse mode and excluded portions.
5. Choose exactly one approach: `greenfield`, `reference`, `integrate`, or
   `fork`. Explain why the selected option is safer and simpler than the viable
   alternatives for this project.
6. Record the result in `docs/open-source-assessment.md` before implementation.
   Keep the record to a concise table for simple projects; use fuller evidence
   and mitigations for standard or complex projects.

## Reuse Safeguards

- Treat popularity as a discovery signal, not proof of suitability or safety.
- Treat a missing, ambiguous, or incompatible license as a stop condition for
  copying, integrating, adapting, or forking code. At most, record high-level
  ideas without copying protected expression.
- Preserve required license texts, notices, attribution, modification notices,
  and source-offer obligations.
- Do not present the assessment as legal advice or a security guarantee. Cite
  sources, label uncertainty, and recommend specialist review when obligations
  or risk are material.
- Research is read-only by default. Obtain explicit approval before cloning or
  downloading a repository, installing a dependency, copying code, creating a
  fork, or otherwise changing local or remote state.
- If a stale or vulnerable candidate is still selected, record the reason,
  affected surface, mitigation, and replacement or update plan.

## Decision Meanings

- `greenfield`: implement independently; record candidates and why they were not
  reused.
- `reference`: learn from public documentation or broad architectural ideas;
  record sources and do not copy code unless separately approved and licensed.
- `integrate`: consume an approved dependency or copy a narrowly identified,
  compatible portion while satisfying all obligations.
- `fork`: preserve upstream history and license, document divergence, and plan
  how upstream security and maintenance changes will be monitored.
