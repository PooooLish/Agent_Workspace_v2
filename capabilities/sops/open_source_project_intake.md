# Open Source Project Intake

Use this procedure before implementing a new software project.

## 1. Define the Search

Record the problem, required capabilities, target stack, constraints, and search
date in the project's `docs/open-source-assessment.md`.

## 2. Gather Current Evidence

Search the web and relevant source hosts using read-only access. Prefer primary
sources: repository README and license files, releases, security policy or
advisories, issues, commits, and official documentation. Shortlist three to five
viable candidates when available; otherwise record the search coverage and gap.

## 3. Evaluate Candidates

For each candidate, record:

- exact URL and reviewed version, tag, or commit;
- license compatibility, attribution, notices, redistribution, and copyleft
  obligations;
- maintenance activity, release cadence, issue health, and maturity;
- advisories, dependency concerns, unsafe defaults, and mitigations;
- technical fit, architecture, tests, documentation, and integration cost;
- intended reuse mode and excluded portions.

Popularity alone is not evidence of fitness or safety. Missing, ambiguous, or
incompatible licensing excludes code copying, integration, adaptation, and
forking.

## 4. Decide

Choose one approach:

- `greenfield`: implement independently after recording why reuse was rejected;
- `reference`: use documentation or high-level ideas without copying code;
- `integrate`: consume an approved dependency or compatible, identified code;
- `fork`: retain upstream history and obligations and plan upstream monitoring.

Keep a simple project's assessment to a concise table. Add fuller citations,
uncertainties, mitigations, and maintenance planning when risk or reuse is
material.

## 5. Obtain Approval Before Mutation

Research does not authorize cloning, downloading, installing dependencies,
copying code, or creating a fork. Obtain explicit approval before any of those
actions. For approved reuse, preserve required licenses, notices, attribution,
modification notices, source offers, and provenance.

## 6. Start Implementation

Begin only after the assessment states the decision and reuse boundary. Cite
reviewed sources and do not describe the result as legal advice or a security
guarantee.
