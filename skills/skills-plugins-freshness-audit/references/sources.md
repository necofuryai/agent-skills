# Source-specific evidence

Read the section for each source included in the request. Run all commands from outside installed skill/plugin trees. Prefer structured JSON and preserve the observed command, timestamp, and revision in the report or working notes.

## Layout discovery

- Resolve every active Codex user skill root from the current runtime/configuration and verify each exists. Current Codex loads both `~/.agents/skills` (canonical) and the deprecated `${CODEX_HOME}/skills` or `~/.codex/skills`; each is only a candidate until verified. In `~/.agents/skills`, entries installed by `npx skills` are recorded in `~/.agents/.skill-lock.json`; any other entry (a symlink into a skills repository or a snapshot directory, a Git clone) falls under its named section below or, failing that, **Other declared upstreams**. Record which root holds each audited item. A skill name present as separate directories in more than one root is duplicate coverage, because Codex then cannot resolve an explicit `$name` mention.
- Obtain Claude plugin installations from `claude plugin list --json`; do not construct cache paths. Treat entries with the same plugin id but different scopes as distinct installations.
- Obtain Codex marketplaces and plugins from `codex plugin marketplace list --json` and `codex plugin list --json`; do not infer remote marketplace membership from local directory names.
- Inspect symlinks with `lstat`/`readlink` semantics. Resolving a link is useful for target comparison, but retain the literal target and whether it is broken.
- If a required CLI is missing or its JSON cannot be parsed, mark the affected evidence `unknown` and include the failure. Do not substitute a cache scan for authoritative CLI state.

## `mattpocock/skills`

Upstream: `https://github.com/mattpocock/skills`

Matt's skills reach each agent as a plugin, not as standalone skill copies. The upstream install block (`.agents/install-block.md` at the upstream default-branch commit) names one managed route per agent: Claude Code installs `mattpocock-skills@claude-plugins-official`, and Codex installs `mattpocock-skills@mattpocock` from the author's own Git marketplace. Use that file's route table as evidence of the author's routes; when the requester has fixed the managed routes, report a difference from the table instead of re-deriving the route. Its statement that managed routes reinstall only when `version` changes does not describe Codex, which force-reinstalls the plugin cache whenever a marketplace upgrade changes the revision; verify this against the installed Codex release's `core-plugins/src/manager.rs` when the distinction matters.

### Upstream inventory

Enumerate every upstream directory containing `SKILL.md`, including engineering, productivity, in-progress, misc, and any categories added later, before applying category assumptions.

Collect:

- upstream default-branch commit SHA;
- every skill identity and relative directory;
- upstream subtree or file hashes and Git file modes;
- the plugin manifest (`.claude-plugin/plugin.json`) and its declared `skills` at every revision an installation is compared with;
- the matching installed inventory of each declared skill directory, including missing files and executable-bit drift;
- the previous upstream inventory when classifying additions, deletions, or renames.

Use GitHub API GETs or one fresh disposable clone. A temporary clone may use `git clone`; do not run `git fetch` or `git pull`. Run `scripts/inventory_tree.py` against each installed declared skill directory and against the same directory in the upstream tree at the revision that installation is compared with. The GitHub tree SHA remains separate evidence; the script's SHA-256 digest is not a Git object id.

Map upstream skills by declared frontmatter name plus relative directory. Report duplicate or ambiguous names instead of choosing by basename. Do not classify unrelated local skills as Matt-derived merely because names or contents resemble upstream.

### Checks shared by both plugins

Coverage is what each installation's own manifest declares at its own installed revision, plus what that agent's loader discovers by default (see each subsection), not the complete upstream inventory. An upstream skill that no installed manifest declares (in-progress, misc, and similar) is expected to be absent; do not report it as missing coverage.

For each enabled installation:

1. Find and parse the plugin manifest at the cache root (currently `.claude-plugin/plugin.json` for both agents; verify rather than assume).
2. Resolve each declared `skills` entry relative to the plugin root without executing files. Record missing entries and paths escaping the plugin root.
3. Compare each declared skill directory's inventory, content, and Git modes with the upstream tree at that installation's installed revision. A difference there is Local drift, except an upstream symlink absent from the Codex cache, which is materialization (see below); record it anyway, because the installed skill lacks that file.
4. Record whether the payload has gained component paths that the agent loads by default without a declaration, because they extend the plugin beyond its skills. Take the list from that agent's plugin reference for the installed release rather than assuming it: for Codex it is currently `hooks/hooks.json`, `.mcp.json`, `.app.json`, and `commands/`; Claude Code's list is longer and includes `agents/` and `bin/`, whose files go on the Bash tool's `PATH` while the plugin is enabled.

Both caches are materialized from the whole repository, so an undeclared `SKILL.md` inside a cache is part of the distribution: unless that agent's loader discovers it by default (see each subsection), do not count it as installed, as a duplicate, or as a removal candidate. Whole-root equality is not the test. These root-level differences are verified materialization, not drift: the Codex cache omits upstream symlinks at any depth (today only the root `AGENTS.md`) and adds `.git/` and `.codex-marketplace-install.json`; the Claude cache adds `node_modules/` and `.in_use/`. A sibling version directory that carries `.orphaned_at` is not an installation. Cache presence alone does not establish an active plugin.

A standalone directory or symlink outside the plugin whose identity belongs to the upstream inventory is not part of either route. Judge it against the agent that reads its skill root: `~/.agents/skills` and `${CODEX_HOME}/skills` belong to Codex, and the Claude skills directory belongs to Claude Code. If that agent's installed manifest declares the skill, the copy is duplicate coverage: the agent exposes the same skill twice, namespaced as `mattpocock-skills:<name>` and plain as `<name>`, possibly at different revisions, and a plain `$<name>` mention reaches the standalone copy. If that agent's manifest does not declare it, report it as an undeclared standalone Matt copy (Local drift). Never create such a copy to fill a gap.

### Codex plugin

Select the exact `mattpocock-skills@mattpocock` entry from `codex plugin list --json` and record its version, enabled state, marketplace name, and marketplace source. The marketplace source should be `https://github.com/mattpocock/skills.git`, configured in `${CODEX_HOME}/config.toml`. For this plugin, this subsection replaces the custom Git marketplace rule in **Codex plugins and marketplaces**.

- The installed payload is that plugin's cache directory, currently `${CODEX_HOME}/plugins/cache/mattpocock/mattpocock-skills/<version>`; verify the path rather than assume it. The installed revision is the `revision` field of `.codex-marketplace-install.json` in that directory.
- The marketplace snapshot that the list output's `source.path` points to (currently `${CODEX_HOME}/.tmp/marketplaces/mattpocock`) is separate evidence. Read its revision from its own `.codex-marketplace-install.json`.
- Read these files; do not run Git inside the cache or the snapshot. Decide which of two revisions is newer by ancestry, using the GitHub compare API or the disposable clone.
- Compare revisions, not only versions. Upstream changes `version` only when it cuts a release, so equal versions can hide different revisions.
- If the manifest drops its `skills` declaration, Codex discovers every `SKILL.md` under `skills/` recursively, so in-progress and misc skills would load. Coverage for that installation is then every such `SKILL.md`; report the change.
- Under this route `~/.agents/.skill-lock.json` holds no Matt entries, and no Codex skill root holds Matt skill directories.

| Observed state | Class |
| --- | --- |
| `${CODEX_HOME}/.tmp/marketplaces/.staging` is not empty, or the snapshot or installed revision changes between reads | Unknown: an upgrade is in progress |
| installed = snapshot = upstream default-branch commit, and the shared checks pass | Current |
| installed = snapshot, both behind upstream | Update candidate; the next marketplace upgrade at Codex startup brings it |
| installed behind the snapshot | Update candidate, behind its own marketplace |
| a declared skill directory differs from upstream at the installed revision | Local drift |

Codex upgrades Git marketplaces at startup by default, so the installed revision can change without a user command. When the previous verified record names a different revision, treat the change as an external update: record both revisions and run the shared checks on the new payload. Without a previous verified record, the change history is Unknown.

### Claude Code plugin

Select every exact `mattpocock-skills@claude-plugins-official` entry from `claude plugin list --json` and record its scope, version, enabled state, and reported `installPath`. The list output does not report the installed commit; take it from the matching entry (same id, scope, and install path) in `~/.claude/plugins/installed_plugins.json`, field `gitCommitSha`. Equal versions can hide different commits here too. Report any `mattpocock-skills@mattpocock` entry in Claude Code separately as superseded duplicate coverage; this applies to Claude Code only, because the Codex entry with that id is Codex's managed route.

The official catalog pins the plugin to a commit: the `mattpocock-skills` entry's `source.sha` in the materialized `claude-plugins-official` marketplace manifest. That manifest is a local copy that Claude Code refreshes on its own schedule. Record the copy's identity (`.gcs-sha` in the marketplace directory) and age (`lastUpdated` in `~/.claude/plugins/known_marketplaces.json`), and where possible cross-check the pin with a read-only GET of the remote catalog's `.claude-plugin/marketplace.json`. If the remote pin differs from the materialized one, classify against the remote pin (an Update candidate that Claude Code has not materialized yet) and record both. Without a remote GET, scope Current to the materialized catalog and state its `lastUpdated`.

Claude Code scans the default `skills/` directory alongside the declared entries (the plugin reference says a manifest `skills` key "Adds to the default `skills/` scan"), so a direct child `skills/<name>/SKILL.md` loads even when undeclared. Count such a skill as installed for that installation and report its appearance. Today `skills/` holds only category directories, so none loads this way. The reference does not say whether the default scan reaches nested `skills/<category>/<name>/SKILL.md`; record that open question in a note rather than assuming either way, and do not let it change the class, unless the running agent's skill list shows such a skill.

- Installed commit equals the pin and the shared checks pass: Current, with comparison scope "official catalog pin". Report the gap between the pin and the upstream default-branch commit as a note, not as a class.
- Installed commit differs from the pin: Update candidate. Updates come through Claude Code's own plugin update route; never edit the cache.
- A declared skill directory differs from upstream at the installed commit: Local drift.

Codex follows the author's default branch and Claude Code follows the catalog pin, so the two agents can run different revisions, versions, and declared skill sets. That difference is expected: report both revisions and do not align one agent with the other.

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

Compare installed/vendor/upstream file sets, content and Git modes. Author attribution in a NOTICE file can differ from the actual distribution repository. A current legacy snapshot match does not mean the old distribution is actively maintained: [openai/skills](https://github.com/openai/skills) is deprecated. A move to a plugin, different ID, or different root is a separate migration, not a normal update.

`hatch-pet` in the deprecated Codex root is not an `openai/skills` import and not a user custom fork. It is a snapshot of the skill bundled with the ChatGPT application (`/Applications/ChatGPT.app/Contents/Resources/skills/skills/.curated/hatch-pet`; verify the path in the installed build). The application installed it once and controls only its enabled state; it does not resync the copy when its bundle changes. A `[[skills.config]]` entry in `${CODEX_HOME}/config.toml` disables it, and the remote `work-pets` plugin succeeds it. Compare the local inventory with the bundle of the installed application build and record that build's version. Classify any difference as Local drift, not Update candidate, because the copy is disabled, superseded, and has no update route. Say whether the local files changed since the last verified inventory (a local edit) or only the bundle moved (expected for an older install). Do not overwrite, re-enable, or delete the copy. Do not use `openai/skills`' `skills/.curated/hatch-pet` as its update source: that is an older workflow in the deprecated repository.

## `apple-design` snapshot

Upstream: `https://github.com/emilkowalski/skills`, subtree `skills/apple-design`. This is a community source, not an Apple distribution.

The user follows upstream `main` for this skill through a snapshot route. `~/.agents/skills/apple-design` is a symlink to `../upstreams/apple-design-snapshots/<commit>`, a directory that holds only that commit's `skills/apple-design` blobs, written from the fetch-only clone `~/.agents/upstreams/emilkowalski-skills`. `apple-design-snapshots/state.json` records the applied commit, and `~/.agents/upstreams/bin/apple_design_snapshot.py` performs the route's steps. The Claude skills directory reaches the same snapshot through its link to `~/.agents/skills/apple-design`. The symlink, older snapshot directories, and the clone's stale working tree are the route's normal layout, not path migration or drift. The tool writes every snapshot file as mode 0644 by design, so an upstream executable bit is not drift; judge the snapshot by `clean` and the tree comparison, not by per-file Git modes. An `applied` commit that differs from the previous verified record is the route's own update or a person's swap: record both commits and classify by the rules below.

This audit only reads. Of the tool's commands, run only `preflight` and `live`, as `python3 -I ~/.agents/upstreams/bin/apple_design_snapshot.py <command>`, with no `AD_TEST_*` variable set. If the requester gives an expected sha256 for the tool, check it before each run; on a mismatch, do not run the tool and classify Unknown. Never run `fetch`, `make`, `swap`, `init`, or `bootstrap`, and never run Git commands yourself inside the clone; the tool's own read-only Git calls from `preflight` and `live` are expected. `live` reports the live commit, the applied commit, whether the user has pinned the link, whether a swap was interrupted, the live subtree tree id, and whether the snapshot is unmodified.

For upstream evidence, if the requester has authorized the route's own `fetch` (the scheduled route does), that fetch is the only upstream source for this item: use its `N` and `subtree_tree` once it has run, and make no other GET, `ls-remote`, or clone. In a run that will perform that `fetch`, classify this item after it, not during an earlier audit pass. If the route stops or holds before its `fetch`, this run collected no upstream evidence; say so. Otherwise take the upstream default-branch commit and its `skills/apple-design` tree id from a GitHub API GET or the disposable clone, not from the route's clone, whose remote-tracking ref is only as fresh as its last `fetch`.

Apply the first rule that matches:

1. The tool's hash does not match; `preflight`, `live`, or the route's `fetch` fails or holds (exit 2); or `preflight` reports problems: Unknown. Report the tool output.
2. `clean` is false: Local drift in the snapshot.
3. `interrupted_swap` is true: Unknown. A swap was interrupted, and the route resumes it on its next run.
4. `pinned` is true: the user has pinned the link to another snapshot, and the route does not update while it is pinned. If the requester keeps its recorded class during a pin (the scheduled route does) or no upstream evidence was collected, keep the previously verified class (Unknown if there is none) and say that it predates the pin. Otherwise classify the pinned live tree by rules 5 to 8. Either way, mark the item pinned. Showing how to release the pin (pointing the link back to the `applied` snapshot) is fine; do not propose that the audit or the route replace the pinned snapshot.
5. No upstream evidence was collected: Unknown.
6. `skills/apple-design` is absent upstream: Unknown. Report the removal, and do not propose deleting the snapshot.
7. The live tree equals the upstream tree: Current.
8. Otherwise: Update candidate. Unless the link is pinned, the user's scheduled route applies it after its own checks and waiting period, or holds it for a person; the audit does not apply it. A hold or failure in a later route step (`check`, `diff`, `make`, `swap`, or the check after a swap) keeps this class.

`~/.config/apple-design/accept` is the user's own approval list for the route. Never write it.

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
- **Local drift:** installed content, mode, symlink, manifest coverage, source, or enabled state differs from its expected local relationship. Manifest coverage means declared entries missing from the installed payload; an upstream item the manifest does not declare is not a coverage gap.
- **Unknown:** required evidence was unavailable, ambiguous, or not authoritative.

Report counts and revisions even when nothing changed. For an update candidate, include a concise change summary and state whether additions, deletions, renames, content changes, and mode changes were observed or remain unknown. Recommendations may name the exact follow-up action, but execution waits for explicit user approval.
