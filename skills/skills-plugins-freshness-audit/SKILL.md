---
name: skills-plugins-freshness-audit
description: Non-mutating audit of installed Codex and Claude skill/plugin freshness against declared upstreams. Use for version, hash, file-mode, manifest, symlink, source, or installed enabled-state drift; not for runtime tool exposure, installs, updates, removals, or connector permission management.
license: MIT
---

# Skills and Plugins Freshness Audit

Establish what is current, drifted, or unknown without changing installed state.

## Guardrail

Keep installed or managed roots, Git refs, plugin caches, settings, and permissions unchanged. Reads and network GETs are allowed; a disposable temporary checkout outside managed roots is allowed only when API evidence is insufficient and must be removed afterward. Report that temporary workspace activity separately from installed-state changes.

Never run skill, plugin, package, marketplace, or managed-source install, update, upgrade, remove, pull, fetch, merge, checkout, reset, or chmod commands. Never run `npx skills check`, `npx skills update`, or `npx skills upgrade`. Cleaning up the audit's own verified temporary directory is allowed. Treat every recommended installed-state change as a proposal pending explicit user approval.

This audit is distinct from `plugin-management`, which manages connectors and permissions, and `skill-installer`, which installs skills.

Audit installed metadata such as a plugin's declared enabled state here. When the question is whether a particular session actually loaded or exposed a plugin tool, route that effective-state question to `ai-agent-effective-config-audit`.

## Workflow

1. Discover the live layout from current CLI JSON, manifests, environment/configuration, and symlink metadata. Verify candidate roots exist before using them; historical or conventional paths are hints, not authority.
2. Read [references/sources.md](references/sources.md) for the source being audited and collect every required evidence field. For a declared upstream not listed there, use its generic-source branch. If a CLI schema differs, record the observed schema and avoid guessing mappings.
3. Run `python3 scripts/inventory_tree.py <directory>` first as a metadata-only preflight. Review every path component for `.env`, credential, token, private-key, secret-template, or other secret-bearing names without opening their contents. Build an exact deny list for any path that looks sensitive even if the script's default matcher might miss it.
4. Run the same script with `--hash-content` only on confirmed skill/plugin code, documentation, and assets whose contents the audit is authorized to read. Pass `--skip-content-path <exact-relative-path>` for every path on the preflight deny list that needs an explicit exclusion; the script rejects a misspelled or missing path before hashing. Check that every denied path has a `skipped-*` content status and no content hash. Use `--allow-content-path <exact-relative-path>` only when the user authorized that exact file and purpose; otherwise keep its content status unknown. Apply the same content policy to any temporary upstream checkout. Treat `tree_sha256` as full content evidence only when `content_complete` is true; otherwise it describes a partial inventory and cannot prove freshness.
5. Compare current evidence with upstream and, when requested, the last verified inventory. Absence of a prior inventory makes rename, deletion, and historical-change claims `unknown`.
6. Report confirmed matches, update candidates, local drift, missing or duplicate coverage, and unknowns separately. Include identifiers, local and upstream revisions or versions, tree differences, mode differences, and the evidence gap behind every unknown.

The audit is complete when every discovered in-scope item is accounted for. A **current** or **update candidate** classification requires both local and authoritative upstream evidence. An **unknown** classification is complete only when it names the missing, unauthorized, ambiguous, or non-authoritative evidence and its effect on the conclusion. A command succeeding, a cache directory existing, or an `available` list being empty is not proof that an item is current.
