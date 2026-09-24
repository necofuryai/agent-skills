# agent-skills

Agent skills I use with Claude Code and Codex, written in the [Agent Skills](https://agentskills.io) format: one `skills/<name>/SKILL.md` per skill.

## Skills

| Skill | What it does | Works with |
| --- | --- | --- |
| [`ai-agent-effective-config-audit`](skills/ai-agent-effective-config-audit/SKILL.md) | Trace a coding-agent setting from documented to configured, loaded/effective and observed state, and find the first edge where it stops taking effect. Read-only unless a change is requested. | Claude Code, Codex |
| [`ai-coding-tool-evaluation`](skills/ai-coding-tool-evaluation/SKILL.md) | Compare AI coding tools (Codex, Claude Code, Cursor, ...) on current pricing and limits, privacy, model access, reachability and workflow fit, then give a conditional recommendation. Written in Japanese. | Claude Code, Codex |
| [`chatgpt-project-organization`](skills/chatgpt-project-organization/SKILL.md) | Inventory, classify and move ChatGPT conversations into Projects, backed by a verified, resumable migration ledger. | Codex in the ChatGPT app; other agents need browser access to chatgpt.com |
| [`dependency-pr-lifecycle`](skills/dependency-pr-lifecycle/SKILL.md) | Assess Renovate/Dependabot PR queues and, when explicitly authorized, advance them: exact-head merge, default-branch CI check, queue refresh and release disposition. | Claude Code, Codex (needs `gh`) |
| [`design-decision-review`](skills/design-decision-review/SKILL.md) | Review cross-component design decisions through independent Architect, Advisor and Synthesizer passes, ending in keep/change/reject decisions with completion and reversal criteria. | Claude Code, Codex |
| [`skills-plugins-freshness-audit`](skills/skills-plugins-freshness-audit/SKILL.md) | Read-only audit of installed Codex and Claude Code skills and plugins against their declared upstreams: version, tree hash, file mode, manifest, symlink and enabled-state drift. | Claude Code, Codex (needs Python 3) |

## Install

```bash
npx skills add necofuryai/agent-skills
```

The installer asks which skills to take and which agents to install them for. To take one skill, pass `-s <name>`. skills 1.7.0 silently ignores the `--skill=<name>` form, so combined with `-y` it installs every skill.

Some skills hand off to skills that are not in this repo. Without them the hand-off step is skipped; nothing else breaks.

- [`mattpocock/skills`](https://github.com/mattpocock/skills): `diagnosing-bugs`, `code-review`, `codebase-design`, `research`, `prototype`, `grilling`
- Codex system skills and plugins: `openai-docs`, `skill-installer`, `plugin-management`

## How I use this repo

I keep a clone at `~/dev/agent-skills` and edit the skills in place. `scripts/link.sh` links each skill into the directories the two tools read:

- `~/.agents/skills/<name>` for Codex
- `~/.claude/skills/<name>` for Claude Code, which does not read `~/.agents/skills`

Skills named in `scripts/claude-exclude.txt` are linked for Codex only. `scripts/link.sh --check` reports missing or broken links, and `--prune` removes links to skills that no longer exist.

The repo deliberately has no plugin manifest (`.claude-plugin/` or `.codex-plugin/`). Without one, `npx skills` finds skills by directory, and Codex keeps the plain skill names when it reads them through the symlinks.

`skills-plugins-freshness-audit/references/sources.md` names the upstreams I audit (`mattpocock/skills` and two writing-skill gists) as worked examples. Its "Other declared upstreams" section is the general procedure.

## Tests

```bash
python3 -m unittest discover -s skills/skills-plugins-freshness-audit/tests
```

## License

[MIT](LICENSE). Each `SKILL.md` also declares `license: MIT` in its frontmatter, because installers copy only the skill's own folder and leave the repository's LICENSE file behind.
