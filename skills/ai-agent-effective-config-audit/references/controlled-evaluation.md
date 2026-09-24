# Controlled Evaluation

Read this reference only when runtime behavior is needed to distinguish effective-configuration hypotheses, especially for subagent inheritance or tool availability. Static inspection and resolved-config evidence remain the default.

## Admission gate

State one configuration hypothesis and one observable outcome that could support or refute it. A probe is warranted only when:

- the outcome matters to the audit;
- direct loaded/effective evidence is absent or insufficient;
- the probe can avoid live services, secrets, destructive commands, and unrelated writes; and
- the user's authorization covers any temporary configuration variation, new process, or persistent task the design requires.

Without authorization to vary configuration, run at most a single-condition observation and label it non-causal. Do not present an audit-only observation as proof that a different setting would change behavior.

## Matched design

Define the result measure before running the probe. Freeze everything except the candidate setting: product and version, model when it is not the variable, reasoning level, prompt, tool catalog, permissions, parent instructions, workspace fixture, initial files, and session lifecycle.

For a baseline/treatment comparison:

1. Capture fingerprints for the relevant configured and loaded/effective state in both conditions.
2. Start each condition across the same documented fresh-process or fresh-session boundary.
3. Use an isolated, inert fixture and identical task text. Alternate condition order when order effects are plausible.
4. Record raw outcomes and traces before interpreting them. Repeat stochastic probes enough to support the strength of the claim; one run establishes an observation, not a general causal effect.
5. Account for failed, timed-out, interrupted, and missing-trace runs instead of silently discarding them.

Only the candidate setting may differ. If the effective-state fingerprint also differs in model, tools, permissions, guidance, repository state, or lifecycle, the pair is not matched and the causal result is inconclusive.

## Subagent tool-use probe

Separate three questions that are often conflated:

1. Was the tool exposed to the subagent?
2. Did the subagent choose and call it?
3. Did the call contribute to the requested outcome?

Use a local read-only or mock tool with a deterministic sentinel result and a small fixture that makes the tool relevant without explicitly commanding a call. Keep parent delegation text and child task identical across conditions. Capture the child session's actual tool catalog and trace when the product exposes them; the parent's catalog or final prose is not evidence of child availability.

Score only predeclared observables such as tool exposure, call count, argument validity, sentinel recovery, evidence use, and task completion. Avoid impressionistic quality scores. A missing call with an exposed tool is an observed choice; a missing call when exposure is unknown cannot diagnose tool-use behavior.

## Completion

A controlled evaluation is complete when the hypothesis, variable, frozen factors, lifecycle boundary, fixture, all runs, raw evidence locations, and limitations are accounted for. Classify the result as supports, refutes, or inconclusive. Feed that classification back into the main four-stage ledger; it does not replace loaded/effective evidence.
