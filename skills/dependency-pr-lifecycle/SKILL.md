---
name: dependency-pr-lifecycle
description: Assess or advance GitHub Renovate and Dependabot PRs when the request involves readiness, queue ordering, exact-head merge, post-merge CI, queue refresh, or release disposition. Excludes code fixes inside a dependency PR and ordinary feature PR review.
license: MIT
---

# Dependency PR lifecycle

Move each dependency PR through live, evidenced states without carrying stale GitHub results across a changed head or base branch.

## Establish the boundary

- Identify the repository, default branch, bot PRs in scope, and requested outcome: readiness assessment, a named merge, queue processing, or release disposition.
- Read the repository's current `AGENTS.md`, dependency policy, branch rules, and release runbook. Repository rules decide the gates; this skill supplies the lifecycle.
- Confirm that each item is a Renovate or Dependabot dependency update from current GitHub metadata. Route ordinary feature PR review to `code-review`.
- Keep readiness analysis, posting an approval review, merge, push, tag, release creation, and package publication as separate actions. Authorization for one does not authorize another.

Proceed when the scope, repository policy, and authorized terminal state are explicit.

## Build a current queue ledger

For every in-scope PR, record:

- PR number and URL, base branch, automation actor, update type, and changed files;
- current head SHA, current base-branch commit SHA, merge base when behind/dependency ordering matters, mergeability, required checks, review state, unresolved threads, and repository-specific timing gates;
- whether the change affects runtime behavior, distributed artifacts, only development/toolchain inputs, or remains unclear.

Use the live head SHA as the identity of the reviewed candidate. Treat missing or inaccessible evidence as unknown, not as a passing gate.

Track this state sequence:

`discovered -> head and base pinned -> repository gates satisfied -> merge authorized -> exact head merged -> default-branch CI verified -> remaining queue refreshed -> release disposition recorded`

Enter a state only after its evidence is observed. A changed head or base commit invalidates downstream readiness and returns the PR to current-head and current-base verification.

## Decide or advance

- For assessment-only requests, report each PR's current state, blocker, safe ordering constraints, and next action without changing GitHub.
- For a mixed request that includes diagnosing or fixing code in a dependency PR, complete that implementation and its local validation through the appropriate workflow first. Then discard the prior GitHub ledger, re-fetch the new head and base, and enter this lifecycle for the separately authorized review or merge transition.
- Choose queue order from dependency relationships, shared lockfiles, security urgency, compatibility risk, and repository policy. Do not assume oldest, smallest, or greenest is automatically first.
- Before any authorized merge, read [advancing-the-lifecycle.md](references/advancing-the-lifecycle.md) and apply its fresh-head, exact-merge, default-CI, refresh, and release rules.
- After each merge, verify the default branch before advancing another PR unless the repository explicitly defines and the user authorizes a different batching policy.

## Stop conditions

Stop before mutation, preserve the ledger, and report the exact blocker when:

- the head or base changed after verification;
- a required check, approval, latest-push approval, review thread, stability window, or mergeability gate is unresolved;
- repository rules required for the requested readiness or merge transition are missing or materially ambiguous;
- fresh GitHub state cannot be retrieved, the exact-head guard is unavailable, or access/rate limits make the result uncertain;
- default-branch CI fails, is cancelled, or cannot be tied to the merged commit;
- the next transition would require an approval review, bot command, merge, push, release, or publication that was not explicitly authorized.

Do not repair, rebase, recreate, close, comment, label, assign, delete a branch, or perform any other GitHub write merely to clear a stop condition unless that exact external action is separately requested.

## Completion

An assessment is complete when every in-scope PR has a live-head and live-base disposition, supporting gate evidence, decision-changing unknowns, and a next action. An authorized queue run is complete only when every in-scope PR is accounted for as merged, blocked, or skipped by explicit user scope or repository policy with the reason recorded; every performed merge is tied to the verified head and base; its default-branch result is known; the remaining queue has been refreshed; and a release disposition of required, not justified, or unresolved is recorded separately from release execution. A missing release contract makes that disposition unresolved; it does not by itself block an otherwise authorized merge whose repository gates are established.

## Routing checks

This skill should activate for requests such as:

- "Review all open Renovate and Dependabot PRs, put them in a safe order, and tell me which can merge."
- "Merge this Dependabot PR if its current head satisfies the repository gates, then check whether a release is needed."

It should not activate for:

- "Review this feature PR against its specification." Use `code-review`.
- "Fix the failing test in this dependency PR." Diagnose or implement the code change first.
- "Fix this Renovate failure and merge it when green." Diagnose and implement first, then start a fresh lifecycle assessment; the merge still requires explicit authorization.
- "Publish version 2.1.0." Use the repository's release workflow after a release is already authorized.
