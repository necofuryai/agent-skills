---
name: ai-agent-effective-config-audit
description: Audit effective configuration for coding agents when documented expectations, declared values, loaded state, and observed behavior may differ. Use for model/context, subagent inheritance, global guidance, hook discovery or invocation, precedence, reload boundaries, or ignored settings; excludes product comparisons, specification-only questions, and failures after configured code has started running.
license: MIT
---

# AI Agent Effective Config Audit

Trace each requested setting through four distinct evidence states:

1. **Documented** — what the current product version says the setting means, where it applies, its precedence, and when it loads.
2. **Configured** — the declared value, its source and scope, and every relevant override.
3. **Loaded/effective** — the value the target process or session actually resolved.
4. **Observed** — the behavior produced by that same process or session.

Treat a later state as separate evidence, not as proof of an earlier one.

## Route the request

Use this skill for effective-configuration questions and for an explicitly requested configuration change whose effect must be verified. Route product selection, pricing, privacy, or workflow comparisons to `ai-coding-tool-evaluation`. Route a question that only asks what an OpenAI or Codex setting officially means to the system-provided `openai-docs` skill when it is available (Codex); within this audit, use it, or current official OpenAI documentation directly, when current OpenAI documentation is one evidence layer.

Use this skill when a declarative hook, tool, or plugin may not be discovered, loaded, exposed, or invoked. Once the configured code is demonstrably running and then exits, throws, or produces the wrong result, route that execution failure to `diagnosing-bugs`. For a chezmoi-managed agent setting, use `chezmoi-mise-change-verify` for the source -> rendered -> live transition and this skill for documented -> configured -> loaded/effective -> observed; preserve each skill's separate authorization boundary.

An audit request is read-only. It authorizes inspection and bounded diagnostics, not configuration edits, restarts, new persistent tasks, dependency changes, or hook installation. If the user explicitly requests a change, change only the named behavior and preserve unrelated configuration. A change request does not by itself authorize interrupting or restarting an application, creating another user-visible task, or altering another persistent scope.

## Audit

### 1. Fix the claim and target

Identify the product, installed version, execution surface, exact setting or behavior, configuration scope, target session or subprocess, and expected result. Record whether the request is audit-only or includes a specific change. Ask when an unknown target, path, scope, or desired value would change the conclusion; do not silently choose one.

Map the relevant lifecycle before interpreting files: discovery paths, precedence, project trust, environment or CLI overrides, load time, reload boundary, and parent-to-subagent inheritance. Product documentation establishes an expectation, not effective state.

### 2. Build the evidence ledger

For every requested setting, report this matrix or an equivalent mapping:

| Stage | Required evidence |
| --- | --- |
| Documented | Current version-specific source for meaning, scope, precedence, and reload behavior |
| Configured | Relevant declared values, exact origins, and the winning precedence path |
| Loaded/effective | Resolved-config output, startup diagnostics, session metadata, or another direct load signal |
| Observed | Reproducible behavior from the same version, surface, workspace, and session lifecycle |

Inspect only the relevant keys and evidence surfaces. Do not open `.env` files, credentials, tokens, private keys, secret templates, or other secret-bearing files or values unless the user authorizes that exact file and purpose. Prefer schema, key names, file metadata, or a product config API that omits or redacts secret values. If the requested conclusion would require reading an unauthorized secret-bearing value, mark that stage unknown and report the evidence boundary. Never echo credentials into commands, logs, or reports.

A file containing a value proves only **configured**. A successful reload command proves only that the command returned successfully. Missing diagnostics leave **loaded/effective** unknown.

Use current primary documentation for version-sensitive claims. For OpenAI and Codex, use the system-provided `openai-docs` skill when it is available (Codex); otherwise use current official OpenAI documentation directly. Record the exact product version and observation time so documentation drift is visible.

### 3. Locate the first broken edge

Reconcile the ledger in order: documented -> configured -> loaded/effective -> observed. Classify the earliest supported mismatch, such as unsupported or renamed schema, wrong scope or file, a higher-precedence override, stale session, non-inherited subagent state, hook lifecycle mismatch, runtime defect, or insufficient evidence. Keep confirmed facts, inferences, and unknowns distinct.

Use direct resolved-state evidence before behavioral inference. Do not infer a subagent's model, context, guidance, permissions, or tools from its parent. When static evidence cannot distinguish plausible effective-state hypotheses and behavior is material, read [controlled evaluation](references/controlled-evaluation.md) and run only a bounded, side-effect-controlled probe.

### 4. Apply an explicitly requested change

Capture the pre-change ledger, make the smallest reviewable edit at the authoritative source, and show the exact changed key or hook. Follow the documented lifecycle boundary with only the actions authorized by the request. A non-disruptive fresh child process used for ordinary validation is allowed; an application restart, interruption, or new user-visible task requires explicit authorization. When that boundary is not authorized or cannot be completed, stop after the source change, report the exact pending lifecycle step, and leave the effective result unverified. Otherwise rebuild the loaded/effective and observed stages in the new lifecycle, reusing the same observation so pre/post results are comparable. Report rollback instructions.

## Observable completion

The audit is complete only when every requested setting has an accounted-for row across all four stages, with unavailable evidence marked unknown; the applicable precedence and lifecycle are explicit; the first proven mismatch is stated when supported; and the report says whether any state changed. If a decision-critical edge is unknown, the overall disposition is **inconclusive**, not “no mismatch found.” Only a complete ledger may support the conclusion that no mismatch was observed. For an authorized change, completion additionally requires the exact minimal diff, the required authorized reload or fresh-session boundary, and a post-change observation from that new lifecycle. Tool success, a visible config value, or a plausible behavior alone is not completion.

## Routing examples

Applies:

- "Codex says one model is configured, but which model did this new task actually load?"
- "Does my global context setting reach subagents, or is a project value winning?"
- "This Claude Code hook is declared but never fires; find which lifecycle edge fails."
- "Change this one global guidance setting and verify it in a fresh session."

Does not apply:

- "Should I pay for Codex or Claude Code?" -> `ai-coding-tool-evaluation`
- "What does the current Codex `model_reasoning_effort` option mean?" -> system `openai-docs`
- "Implement a new repository hook." -> the repository's normal implementation workflow
- "Benchmark which agent is best at using tools." -> a comparison or evaluation workflow unless a specific configuration hypothesis is being audited
