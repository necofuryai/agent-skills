---
name: design-decision-review
description: Review non-trivial cross-component decisions about systems, workflows, operations, repository policy, or information architecture—especially ownership, lifecycle, state transitions, and automation boundaries—through independent Architect, Advisor, and Synthesizer passes. Use when proposed mechanisms may anchor the answer or viable designs must converge; not for routine implementation, research-only work, code review, interactive grilling, prototypes, or single-module interface design.
license: MIT
---

# Design Decision Review

Reach a defensible design decision without mistaking the user's proposed mechanism for a requirement or manufacturing disagreement for its own sake.

## 1. Frame the decision

Separate the input into:

- explicit goals, constraints, prior decisions, and authorization boundaries;
- observed failures and current evidence;
- proposed mechanisms or options;
- inferences and unknowns that could change the decision.

Preserve explicit goals and decisions. Treat proposed mechanisms as hypotheses unless the user has explicitly fixed them as requirements.

Complete this step when the decision outcome, material constraints, evidence, and decision-changing unknowns are clear enough to compare designs. Ask only for missing user facts that materially affect the decision; continue independent work that does not depend on them.

## 2. Produce an independent Architect proposal

When independent agent context is available, give the Architect a self-contained evidence bundle containing the goals, facts, constraints, observed failures, and success conditions, but omit the user's proposed mechanisms. In Codex collaboration, use a fresh subagent with no inherited turns when practical.

The Architect returns one coherent design with:

- the actual outcome it optimizes;
- its governing mechanism and important boundaries;
- the smallest viable implementation sequence;
- assumptions, observable success criteria, and reversal conditions.

If an independent pass is unavailable, draft the evidence-first candidate before evaluating the user's mechanisms and disclose that it was not independently generated.

Complete this step when the candidate can be evaluated without referring to hidden reasoning.

## 3. Run an independent Advisor review

Give a separate Advisor the evidence bundle, the Architect proposal, and the user's proposed mechanisms. Ask it to evaluate only material issues:

- omitted goals, constraints, or credible alternatives;
- unsupported assumptions or invented precision;
- operational load, lifecycle, ownership, and state transitions;
- downstream effects and failure modes;
- a simpler viable design;
- facts that would reverse the recommendation.

The Advisor may agree with the Architect. Agreement is a valid result; do not require novelty, a fixed number of alternatives, or adversarial criticism. Every finding must explain how it could change the recommendation, implementation order, or boundary.

Complete this step when each material finding is supported by the supplied evidence or clearly labeled as an inference or unknown.

If an independent Advisor cannot be obtained, do not silently substitute an external provider. Perform a clearly labeled self-review and report the result as `degraded, not independently validated`.

## 4. Synthesize the decision

Compare the user's mechanisms, the Architect proposal, and the Advisor findings against the same goals and constraints. For each material point, decide:

- **keep**: preserve it and state why;
- **change**: retain the useful part and state the required modification;
- **reject**: omit it and state the decisive reason.

For each material Advisor finding, record **resolved**, **rejected**, or **deferred**. A deferred finding must name the missing evidence and whether the recommendation remains conditional until it is obtained.

Return:

1. the recommended design and actual outcome;
2. the material keep/change/reject decisions;
3. implementation order with dependencies, ownership, or state transitions when relevant;
4. observable metrics and completion criteria;
5. unknowns and conditions that would reverse the decision.

Prefer the simplest design that satisfies the evidence. If the user's original design is best, keep it without adding complexity to demonstrate independence.

## Boundaries

- The three roles may use the same model in independent contexts. A different vendor is not required.
- Do not send content to an external model or provider without explicit authorization and an available workflow that preserves the stated data boundary.
- A consultation or review request authorizes analysis, not implementation, file edits, external writes, or publication.
- Use `codebase-design` as specialist reference for module interfaces and seams when relevant. `research` and `prototype` are separate work stages that may create artifacts or code; execute them only when the current request separately authorizes that work. Use `grilling` instead when the user explicitly requests an interactive stress test.
- Distinguish observed facts, inference, recommendations, and unresolved questions in the final answer when the distinction matters.

## Evaluation

When creating or changing this skill, changing its prompt protocol, or comparing models for this workflow, read [references/evaluation.md](references/evaluation.md) and run the fixed forward evaluation. Do not load it for ordinary consultations.

Report **independently validated** only when both the independent Architect and independent Advisor passes were obtained. Otherwise report **degraded, not independently validated**. In either state, every proposed mechanism must have a keep/change/reject disposition, every material Advisor finding must be resolved/rejected/deferred, and the recommendation must include observable completion and reversal conditions.
