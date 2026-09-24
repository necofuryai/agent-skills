# Design decision review forward evaluation

Use this reference only to evaluate a change to the skill or its prompt protocol, or when the user asks for a model comparison. It is not part of an ordinary design decision review.

## Controls

- Compare the baseline and candidate with the same model, reasoning effort, tools, surrounding context, and output limit.
- For the first installation, the baseline is the same task without this skill. For an update, the baseline is the last adopted skill version. Record SHA-256 hashes of both conditions.
- Use fresh sessions. Do not show one condition the other condition's output.
- Run each fixture at least three times per condition for an adoption decision. A one-run pilot may reject a candidate but cannot certify it.
- Generation sessions receive only the condition's `SKILL.md` content and the fixture text. They must not receive this evaluation reference, the rubric, reference signals, another condition's output, or model identities.
- Inspect the execution trace separately from answer quality. A candidate run must have a distinct Architect context, a distinct Advisor context, and an Architect prompt that omits the user's proposed mechanisms. An update baseline must satisfy the role contract of its recorded baseline version. A first-install baseline without a skill is valid without those roles; verify only that it used the fixed tools and context and did not receive candidate instructions, rubric, or reference signals. A missing required role or leaked proposal invalidates the affected run and it must be rerun.
- Remove model and condition identifiers, randomize answer labels, and use two independent blind graders.
- Give graders only the anonymized final answers, scoring rubric, and grader-only reference signals. Do not give them condition identities or generation traces.
- Do not reward verbosity, headings, the number of alternatives, or exact reference wording.
- Adjudicate a total-score difference greater than three points, a fatal-failure disagreement, or a different winner with a human reviewer.
- If adjudication cannot resolve a disagreement, report the adoption decision as indeterminate and stop.
- The workflow does not authorize external-provider calls. Use an external model only when the user explicitly authorizes that provider and content for the evaluation.
- Keep run artifacts outside the target repository unless the user explicitly asks to retain them. Record the date, effective model, effort, tools, and harness with the evaluation report.

## Scoring rubric

Score each dimension from 0 to 4. Each answer has a maximum of 20 points; the three fixtures total 60.

| Dimension | 0 | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- | --- |
| Purpose and problem framing | Repeats the proposed mechanisms | Superficially renames the problem | Notices the underlying issue but does not change the design | Reframes the outcome and applies it | Identifies the causal bottleneck and what does not need optimization |
| Independent derivation and option handling | Mirrors the user's proposed outline | Rearranges or renames the proposals | Derives an evidence-first insight but does not apply it | Produces a design that follows from the evidence and considers a simpler or different mechanism when credible | Clearly separates requirements from solution hypotheses and either compares credible mechanisms or explains why the original mechanism remains best |
| Critical selection | Accepts or rejects everything | Gives generic pros and cons | Partly evaluates options but leaves disposition unclear | Uses causal reasons to keep, change, or reject | Also captures interactions, downstream effects, and reversal conditions |
| Convergence and executability | Lists ideas | Gives an abstract direction | Has a direction but lacks sequence, ownership, state, or metrics | Produces a coherent order and observable criteria | Produces the smallest testable design with stopping and review conditions |
| Restraint and factual discipline | Invents facts or forces contrarian complexity | Relies on unsupported assumptions | Labels some uncertainty but expands scope | Preserves useful proposals and distinguishes facts from assumptions | Remains proportionate in the negative control and changes only what evidence requires |

Fatal failures are: inventing a material fact, violating an explicit constraint, omitting a requested decision, treating the user's proposed mechanisms as fixed requirements without evaluating them on a challenge fixture, or forcing an unjustified redesign in the negative control.

## Aggregation

1. Each grader scores every dimension for every answer.
2. Resolve required adjudications before aggregation.
3. Average the two grader scores for each dimension and answer.
4. For each fixture and condition, take the median total and median dimension scores across the three runs.
5. The condition total is the sum of the three fixture median totals, with a maximum of 60.

Any fatal failure in a candidate run rejects the candidate. Report baseline fatal failures separately; they do not make a candidate acceptable.

## Adoption gate

Adopt a prompt or workflow change only when:

- its sum of median totals across the two challenge fixtures improves by at least four points over baseline;
- its median purpose/problem-framing and critical-selection scores are each at least 3 on both challenge fixtures;
- its median restraint-and-factual-discipline score is at least 3 on the negative control;
- its negative-control median total is no more than two points below baseline;
- there are no fatal failures.

If the baseline is already near the ceiling and the candidate does not clear the improvement gate, retain the baseline. More instructions without a measured benefit are not an improvement.

## Fixture 1: lifecycle and source of truth

```text
Design next year's document operations for a fictional community workshop group.

The group has 12 volunteers and runs 6-10 irregular events per year. It manages venue entry rules, equipment-vendor contacts, day-of role assignments, and attendee instructions in Markdown. Today it creates folders by event and year, copying the prior year's materials.

Last year, obsolete venue rules caused two incidents. After a coordinator changed, nobody could tell which documents had been verified. Events may be five months apart. The group can spend two hours per week on operations, and one representative is the final approver.

The user proposes: (1) copy last year's folder every January, (2) have AI rewrite all documents monthly, (3) build a dashboard showing document age, and (4) review every document quarterly.

Finish the operating design. You may keep, change, remove, or add mechanisms. Answer in Japanese. Within 900 Japanese characters, give: the actual objective, keep/change/reject decisions, implementation order, success metrics, and only decision-changing assumptions. Do not ask questions.
```

## Fixture 2: observed bottleneck over proposed solution

```text
Design a three-month improvement experiment for a fictional community delivery service.

The service owns 20 electric cargo bikes. Volunteers deliver daily goods. Complaints say that bikes are unavailable when needed. The user proposes: (1) buy 10 bikes, (2) require 30-minute reservations, (3) automatically penalize late returns, and (4) build an app showing every bike's state.

During the last eight weeks, an average of 17 bikes were at the depot on weekday mornings, but only seven were usable because the others needed charging or repair. In the evening, bikes remained in outlying areas after one-way deliveries, leaving the central depot short. Deliveries vary from 10 to 90 minutes. Thirty percent of volunteers are uncomfortable with smartphones. The budget can fund either 10 bikes or one year of operational improvement, not both.

Design an experiment that reduces complaints and increases completed deliveries. The proposals are not requirements. Answer in Japanese. Within 900 Japanese characters, give: problem framing, keep/change/reject decisions, experiment order, success and stopping criteria, and only decision-changing assumptions. Do not ask questions.
```

## Fixture 3: negative control

```text
Improve lending operations for 60 board games at a fictional small community center.

The desk handles about 10 loans per day with two staff members. Lending happens only during staffed hours; remote reservation is unnecessary. Wi-Fi is unreliable and there is no budget for new devices. Recent inventory mismatches occurred because returned games were placed on shelves before the return was recorded.

The user proposes: (1) give each game a unique number, (2) make one paper ledger the sole lending record, (3) process loans and returns only at the desk, (4) keep returned games in an unprocessed box until recording is complete, (5) reconcile the ledger and box at closing, and (6) run a weekly full inventory during the first month.

Review the proposal and make it ready to start. Answer in Japanese. Within 900 Japanese characters, give: objective, keep/change/reject decisions, startup sequence, success metrics, and only decision-changing assumptions. Do not ask questions.
```

## Grader-only reference signals

Do not provide these signals to generation sessions.

- **Fixture 1:** Look for a shift from document freshness to verified information at use time, stable sources of truth separated from event artifacts and history, event-driven verification, and human evidence and approval. A dashboard or AI rewriting should not become the objective.
- **Fixture 2:** Look for a distinction between total fleet and effective supply, tests of charging, repair, and redistribution before purchasing, scrutiny of fixed 30-minute slots and automatic penalties, non-smartphone access, and measurement of availability, distribution, completed deliveries, complaints, and operational load. Precise targets must not be invented as facts.
- **Fixture 3:** This is the agreement fixture. A strong answer preserves the proportionate paper, desk, and unprocessed-box design; adds only minimal ownership, handoff, correction, exception, and reconciliation controls; and avoids unjustified apps, AI, devices, or elaborate redesign. A materially different mechanism is not required.

## Scope coverage fixtures

Run these once per condition when the skill description, advertised scope, or role protocol changes. Score them with the same rubric. They do not enter the 60-point adoption delta, but each candidate answer must score at least 15 and have no fatal failure.

### Cross-component architecture

```text
Design feature-flag governance across several fictional web and mobile services. Each repository currently owns YAML flags. The user proposes moving every flag to one central repository, deleting flags automatically after 90 days, letting AI delete unused flags nightly, and building a dashboard.

Observed facts: 38 stale flags and 17 flags without owners were found in six months; about 40% of flags are permanent controls for subscription plans or regulated regions; mobile clients may remain unupdated for more than 30 days; an audit must reconstruct the effective rule at any time during the prior year; a three-person platform team operates the shared tooling while service teams retain feature responsibility.

The proposals are hypotheses. Recommend governance, state transitions, responsibility boundaries, implementation order, success criteria, and reversal conditions. Distinguish facts, inferences, and unknowns.
```

### Repository policy

```text
Design release-runbook policy for a fictional organization with 18 independently deployed repositories. Each repository currently copies a shared template. Six runbooks were stale during incidents last year. Five services have additional regulatory steps, and several runbooks depend on repository-local commands and paths. Service teams own deployments; a two-person platform team owns common tooling.

The user proposes moving every runbook into one central documentation repository, banning local runbooks, and having AI rewrite all runbooks nightly from repository contents.

Decide what to centralize and what to keep local. Give keep/change/reject decisions, ownership and lifecycle, rollout order, observable completion criteria, and conditions that would reverse the design.
```

## Routing checks

Run each prompt in a fresh session without naming this skill. Record whether it was selected and which competing skill, if any, was selected.

The skill should activate for:

- `Decide whether eight services should share one workflow engine or keep service-owned orchestration; compare ownership, lifecycle, failure isolation, migration order, and reversal conditions.`
- `Redesign repository-wide policy for sources of truth, archival history, update triggers, and automation boundaries.`

It should not activate for:

- `The retry design is approved. Change the retry count from two to three and run the affected tests.` — routine implementation.
- `Research the current GitHub ruleset API and save the findings as Markdown.` — `research`.
- `Review this pull-request diff for bugs and repository-standard violations.` — code review.
- `Design the interface between this parser and storage adapter.` — `codebase-design`.
- `Grill me relentlessly about my database migration plan.` — `grilling`.
- `Build a throwaway UI so we can test whether this state model feels right.` — `prototype`.

The candidate passes routing only when both positive prompts select this skill and every negative prompt avoids it.
