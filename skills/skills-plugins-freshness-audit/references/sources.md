# Source-specific evidence

Read the section for each source included in the request. Run all commands from outside installed skill/plugin trees. Prefer structured JSON and preserve the observed command, timestamp, and revision in the report or working notes.

## Layout discovery

- Resolve every active Codex user skill root from the current runtime/configuration and verify each exists. Current Codex loads both `~/.agents/skills` (canonical) and the deprecated `${CODEX_HOME}/skills` or `~/.codex/skills`; each is only a candidate until verified. In `~/.agents/skills`, entries installed by `npx skills` are recorded in `~/.agents/.skill-lock.json`; any other entry (a symlink into a skills repository, a Git clone) falls under **Other declared upstreams**. Record which root holds each audited item. A skill name present as separate directories in more than one root is duplicate coverage, because Codex then cannot resolve an explicit `$name` mention.
- Obtain Claude plugin installations from `claude plugin list --json`; do not construct cache paths. Treat entries with the same plugin id but different scopes as distinct installations.
- Obtain Codex marketplaces and plugins from `codex plugin marketplace list --json` and `codex plugin list --json`; do not infer remote marketplace membership from local directory names.
- Inspect symlinks with `lstat`/`readlink` semantics. Resolving a link is useful for target comparison, but retain the literal target and whether it is broken.
- If a required CLI is missing or its JSON cannot be parsed, mark the affected evidence `unknown` and include the failure. Do not substitute a cache scan for authoritative CLI state.

## `mattpocock/skills`

Upstream: `https://github.com/mattpocock/skills`

Audit all upstream directories containing `SKILL.md`, including engineering, productivity, in-progress, misc, and any categories added later. Enumerate the live upstream tree before applying category assumptions.

Collect:

- upstream default-branch commit SHA;
- every skill identity and relative directory;
- upstream subtree or file hashes and Git file modes;
- the matching local skill inventory, including missing files and executable-bit drift;
- the previous upstream inventory when classifying additions, deletions, or renames.

Use GitHub API GETs or one fresh disposable clone. A temporary clone may use `git clone`; do not run `git fetch` or `git pull`. Run `scripts/inventory_tree.py` against both copies for a content comparison. The GitHub tree SHA remains separate evidence; the script's SHA-256 digest is not a Git object id.

Map upstream skills by declared frontmatter name plus relative directory. Report duplicate or ambiguous names instead of choosing by basename. Do not classify unrelated local skills as Matt-derived merely because names or contents resemble upstream.

### Codex copies

Codex copies are `npx skills`-managed directories under the verified `~/.agents/skills` root. For each `~/.agents/.skill-lock.json` entry whose `source` is `mattpocock/skills`, record `skillPath` and `skillFolderHash` (the upstream Git tree SHA of that skill directory at install time) and compare it with the current upstream tree SHA from a GitHub API GET. A Matt-derived skill that also remains as a separate directory in `~/.codex/skills` is duplicate coverage.

### Claude plugin and complementary symlinks

Select every exact `mattpocock-skills@claude-plugins-official` entry from `claude plugin list --json` and record its scope, version, enabled state, and reported `installPath`. Report any remaining `mattpocock-skills@mattpocock` entry separately as superseded duplicate coverage. Cache presence alone does not establish an active plugin.

For each enabled installation:

1. Find and parse its live plugin manifest (currently conventionally `.claude-plugin/plugin.json`, but verify rather than assume).
2. Resolve each declared `skills` entry relative to the manifest/plugin root without executing files. Record missing entries, paths escaping the plugin root, inventory differences, and file-mode differences.
3. Discover the active Claude skills directory, then enumerate complementary symlinks whose skill identities belong to the upstream inventory. Each expected complement must be a non-broken symlink to the corresponding `npx skills`-managed copy in the verified `~/.agents/skills` root.
4. Compare the union of manifest-declared skills and valid complementary symlinks with the complete upstream inventory. Report missing coverage, duplicate coverage, disabled installations, and plugin/canonical/upstream drift separately.

Do not assume the manifest declares every upstream skill; that is why complementary symlink coverage is audited.

## Gist-backed writing skills

Expected upstream repositories:

- `japanese-tech-writing`: `https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d`
- `cognitive-rhythm-writing`: `https://gist.github.com/k16shikano/eb2929f13ed19c97188393d297be8432`

Locate each skill under every verified skill root that holds it and confirm the resolved directory is a Git worktree before comparing it. An entry in the Claude skills directory that is a symlink to the same worktree is the same copy; a separate directory is a second copy to compare on its own. Record:

- local `HEAD` from `git -C <path> rev-parse HEAD`;
- local worktree status from a read-only status command;
- remote `HEAD` from `git ls-remote <expected-url> HEAD` or the GitHub Gist API;
- repository URL mismatch, dirty local files, and inventory differences when content evidence is requested.

Equal commit ids establish HEAD equality only. Local modifications remain local drift. A failed remote lookup, absent Git metadata, or ambiguous remote HEAD is `unknown`, never “current.”

## Codex plugins and marketplaces

Use both current Codex JSON inventories named in **Layout discovery** above.

For every installed plugin, record the observed plugin id, name, marketplace name, version, installed/enabled state, source kind and identifier/path, marketplace source, and applicable policy fields. Include remote-source plugins even when their marketplace name is absent from the marketplace-list response.

Classify freshness by evidence source:

- OpenAI-managed local or bundled sources: report the current local version and source. Do not infer a newer remote version unless the CLI or an authoritative endpoint exposes one.
- Remote managed sources: report the installed version. If the CLI exposes no authoritative latest version or update status, freshness is `unknown`.
- Custom Git marketplaces: compare the configured revision with the remote revision using read-only API/`git ls-remote` evidence only. Do not run an upgrade.

### Managed distribution evidence and update ownership

Collect these comparisons separately rather than flattening all missing evidence into an update blocker:

| Comparison | Required evidence | What a match establishes |
| --- | --- | --- |
| bundled release assignment | Current application resource manifest, materialized marketplace manifest, installed cache manifest | The installed manifest version matches this application build's assigned bundle |
| remote release assignment | Current server-installed record plus the same source ID's installed cache manifest | The cache manifest version matches the release assigned to this account |
| catalog release observation | Authoritative catalog release version, source ID, fetch timestamp, and verified account/scope binding | Equality to that observed catalog snapshot, with its age stated |
| full payload integrity | Permitted file content, type and mode from the installed and mapped distribution trees, with `content_complete=true` | Complete equality for the stated distribution and content policy |

A release-assignment match does not establish public-latest freshness or full payload integrity. Keep the main Current/Update candidate/Local drift/Unknown classification scoped to the fields actually verified. When the assigned release matches but a latest release cannot be established, report the match and the remaining latest-version evidence gap; do not describe that situation as a failed update.

Preserve the observed CLI schema. In Codex CLI 0.159.2, remote rows project `version = local_version.or(version)` and omit the separate catalog version. Here `local_version` comes from the server-installed record, not a local disk inspection. Compare the CLI value with the cache manifest yourself, and verify this mapping again when the CLI implementation/schema changes. Evidence: [CLI projection](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/cli/src/plugin_cmd.rs), [remote summary](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/core-plugins/src/remote.rs).

If existing `~/.codex/cache/remote_plugin_catalog` metadata is used, preflight its paths first and project only the audited IDs' version/status/policy fields plus `fetched_at`. Do not dump or hash the whole catalog, signed bundle URLs, credentials, or unrelated records. Record cache age and whether its active account/scope binding was verified. Missing entries in a cached catalog are not proof of removal. The current cache TTL is three hours; verify the active implementation before relying on it.

These CLI status commands can refresh catalog metadata on disk. Record any observed discovery-cache activity separately from installed payload/configuration changes. Do not claim the commands are completely side-effect-free. A fresh app-server or public `plugin/list` probe is not a read-only fallback: startup/listing can schedule bundle installation and stale-cache removal. Do not launch that probe inside this audit. Evidence: [listing handler](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/app-server/src/request_processors/plugins.rs), [manager background tasks](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/core-plugins/src/manager.rs), [catalog cache](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/core-plugins/src/remote/catalog_cache.rs).

Remote managed bundles normally reconcile against the server's authoritative installed snapshot. Bundled plugins reconcile against the current application's resources. A generated `bundledContentVariant` can be a supported materialization transform; verify the current transform before calling it drift. Git marketplace upgrade commands are not a general updater for these distributions. Investigate an updater error or an assigned-release/cache mismatch before proposing a reinstall, cache deletion, private RPC, or feature override. Evidence: [remote bundle reconciliation](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/core-plugins/src/remote/remote_installed_plugin_sync.rs).

### Deep research availability

For an explicit `deep-research-work@openai-curated-remote` watch, retain its exact source ID and distinguish installed, available, and absent. Observe another name/ID as a separate candidate until authoritative evidence establishes its relationship. Current application code also defines `deep-research@openai-bundled` behind a `deepResearch` eligibility flag; the declaration and its default value do not prove that flag is effective or that it replaces the remote plugin. Native Work deep research and the specific plugin's distribution are separate evidence surfaces. If the exact plugin is unavailable, report the missing availability evidence rather than inventing a local update error or forcing a feature flag. The account/workspace-dependent product entry points are documented in the [official web-search guide](https://learn.chatgpt.com/docs/web-search).

An empty `available` array proves only that the command returned no available entries under its current semantics. It does not prove every installed plugin is current. When a prior verified report exists, compare plugin name, source, version, and enabled state; otherwise historical change is `unknown`.

## Codex embedded system skills

System skills under the verified deprecated root's `.system` directory are materialized by the active Codex executable. They have no independent package version or per-skill updater.

- Resolve the active executable and its version, then identify the matching authoritative `openai/codex` release commit. The current source mapping is `codex-rs/skills/src/assets/samples/<skill-name>`; verify it for that release rather than guessing from a name.
- Compare the full local inventory with that release's embedded assets after metadata preflight. The `.codex-system-skills.marker` is a distribution fingerprint, not a substitute for content evidence.
- Inspect the release's materialization code when comparing modes. In 0.159.2 the writer uses `fs::write` without preserving source executable flags, so generated regular files can be `100644` even when their source Git mode is `100755`. Record this verified normalization; do not repair it with `chmod` merely to match the source tree. See the [release materializer](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/skills/src/lib.rs).
- Scope Current to the installed executable's distribution. Whether a newer application/CLI release is available is a separate client-update check. Handle updates through the ordinary client distribution route, preserving user release pins and the restart authorization boundary.

## Legacy curated and standalone skill copies

The existing `~/.codex/vendor_imports/skills` Git worktree can retain the authoritative source record for legacy copies. Verify its actual remote, revision, status, and correspondence with installed files before using it. For a verified `https://github.com/openai/skills.git` import, these full-distribution mappings include the wrapper scripts and resources, not just an original author's credited file:

| Installed identity | Source subtree |
| --- | --- |
| playwright | `skills/.curated/playwright` |
| screenshot | `skills/.curated/screenshot` |
| security-best-practices | `skills/.curated/security-best-practices` |
| security-threat-model | `skills/.curated/security-threat-model` |
| sentry | `skills/.curated/sentry` |
| hatch-pet | `skills/.curated/hatch-pet` base only |

Compare installed/vendor/upstream file sets, content and Git modes. Author attribution in a NOTICE file can differ from the actual distribution repository. A current legacy snapshot match does not mean the old distribution is actively maintained: [openai/skills](https://github.com/openai/skills) is deprecated. A move to a plugin, different ID, or different root is a separate migration, not a normal update.

For `hatch-pet`, preserve verified local v2/8x11 functionality, look-direction handling, scripts and tests as a custom fork. Compare the known curated base only to describe upstream differences; do not overwrite the complete local fork to make it equal to that base.

Reviewed installation records can establish `apple-design`'s community source as `emilkowalski/skills`, subtree `skills/apple-design`. Verify the record before applying that mapping to a copy; it is not an Apple-official distribution. Record the initial fixed revision, current content, and an explicit user pin policy separately. If the current copy matches published upstream but differs from the initial artifact and the update trail is unclear, report both facts and preserve it. Do not infer permission to repin or overwrite it from a latest-content match.

## Other declared upstreams

For a skill or plugin outside the named sources, first locate its own declared source in a manifest, lockfile, package metadata, Git remote, or authoritative distribution record. Do not infer provenance from a matching name or directory layout.

Collect the same minimum evidence:

- installed identity, source kind, version or revision, enabled state, and local inventory;
- authoritative upstream identity and current revision or version;
- the distribution mapping between the upstream subtree or artifact and the installed files;
- previous verified inventory only when historical additions, deletions, or renames are requested.

Use a network GET, source API, `git ls-remote`, or one disposable clone appropriate to that declared source. If provenance, mapping, or an authoritative latest revision cannot be established, classify freshness as `unknown` rather than designing a source-specific heuristic during the audit.

## Result vocabulary

- **Current:** complete local and authoritative upstream evidence match for the stated fields.
- **Update candidate:** authoritative upstream evidence differs from installed evidence.
- **Local drift:** installed content, mode, symlink, manifest coverage, source, or enabled state differs from its expected local relationship.
- **Unknown:** required evidence was unavailable, ambiguous, or not authoritative.

Report counts and revisions even when nothing changed. For an update candidate, include a concise change summary and state whether additions, deletions, renames, content changes, and mode changes were observed or remain unknown. Recommendations may name the exact follow-up action, but execution waits for explicit user approval.
