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

An empty `available` array proves only that the command returned no available entries under its current semantics. It does not prove every installed plugin is current. When a prior verified report exists, compare plugin name, source, version, and enabled state; otherwise historical change is `unknown`.

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
