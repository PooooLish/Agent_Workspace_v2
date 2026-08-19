---
name: dependency-and-security-review
description: Use when adding, upgrading, replacing, or removing a third-party package, SDK, plugin, action, container image, build tool, or transitive dependency, especially when provenance, licensing, vulnerabilities, maintenance, install scripts, permissions, or lockfile changes affect adoption risk.
---

# Dependency and Security Review

## Core principle

Adopt the smallest justified dependency only after its identity, obligations,
and current risk are understood. Popularity is not assurance.

## Review workflow

1. **Establish need.** State the capability required, why existing code or an
   existing dependency cannot provide it, and the cost of implementing the
   minimal alternative locally.
2. **Verify identity.** Record the exact package, publisher, canonical source,
   registry, selected version or digest, release date, and checksum or lockfile
   identity when available. Check for typosquatting and ownership changes.
3. **Confirm licensing.** Read the license in the selected source and published
   artifact. Check notices, attribution, copyleft, redistribution, patent, and
   commercial-use obligations for direct and material transitive dependencies.
   Missing, ambiguous, or incompatible licensing blocks adoption.
4. **Check current security evidence.** Consult authoritative registries,
   project advisories, OSV or equivalent vulnerability databases, release
   notes, and known malicious-package reports. Record the lookup date and
   affected versions. Do not treat a package-manager audit as complete proof.
5. **Assess maintenance and fit.** Review recent releases and commits,
   unresolved critical issues, deprecation, supported runtimes, API stability,
   required permissions, network access, native code, data handling, and
   operational impact.
6. **Inspect installation effects.** Review install hooks, generated files,
   binaries, build steps, dependency count, and lockfile diff. Do not install,
   download, execute, or update a lockfile without explicit approval.
7. **Test the boundary.** After approved installation, verify only the required
   capability, failure behavior, compatibility, and resource/security limits.
8. **Decide and record.** Choose `approve`, `approve-with-conditions`, `defer`,
   or `reject`; record the pinned version, evidence, conditions, update owner,
   and removal or rollback path.

## Minimum report

| Area | Evidence |
| --- | --- |
| Need | Required capability and alternatives |
| Identity | Package, source, publisher, version/digest |
| License | Direct and relevant transitive obligations |
| Security | Current advisories and lookup date |
| Maintenance | Release activity, support, deprecation |
| Runtime | Permissions, scripts, native/network/data behavior |
| Change | Manifest and lockfile impact |
| Decision | Outcome, conditions, pinning, rollback |

## Decision rules

- Reject unknown provenance, malicious indicators, or incompatible licensing.
- Defer when current advisory, transitive, or maintenance evidence is missing.
- Prefer an existing dependency or standard library when it meets the need.
- Pin reproducibly according to the ecosystem; do not claim reproducibility
  without inspecting the resolved lockfile or digest.
- Treat major upgrades and maintainer or package-ownership changes as fresh
  reviews, not routine version bumps.

## Common mistakes

- trusting downloads, stars, or README examples as security evidence;
- checking only direct dependencies;
- ignoring install scripts, permissions, native binaries, or remote code;
- accepting an audit's zero findings without checking coverage and freshness;
- mixing dependency adoption with unrelated upgrades or lockfile churn.
