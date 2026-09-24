# Advancing the dependency PR lifecycle

Read this reference only when the request may advance GitHub state or asks for the post-merge release disposition.

## Authorization ledger

Record each requested external transition independently:

| Transition | Required authorization |
| --- | --- |
| Post an approval or other review | Explicit request to submit that review |
| Merge a PR | Explicit request to merge that PR or the defined queue |
| Send a bot command, rebase, recreate, close, or comment | Explicit request covering that write |
| Apply labels or assignments, dispatch/rerun/cancel workflows, enable auto-merge, enqueue a merge queue, update a branch, delete a branch, or perform any other GitHub write | Explicit request covering that exact write |
| Push a branch or tag | Explicit request to push |
| Create a GitHub Release or publish a package | Explicit release or publication request |

If the user authorized a later transition without an earlier required transition, complete all read-only preparation and stop at the missing authorization boundary.

## Pin and merge the exact candidate

Immediately before a merge:

1. Re-query the PR's current head SHA, base branch and current base commit SHA, merge base when relevant, mergeability, required checks, reviews, latest-push approval if applicable, unresolved threads, and timing gates.
2. Compare the observed head and base commit with the ledger. If either differs, discard the prior readiness result and assess the new candidate.
3. Confirm the repository's permitted merge method and any queue-specific ordering dependency.
4. Merge only with an exact-head guard such as API `expected_head_sha` or CLI `--match-head-commit`. If the available path cannot bind the action to the verified SHA, stop.
5. Reopen the PR and default branch to verify the merge result and resulting commit. A success response alone is not proof of the final state.

Do not post an approval review merely because the repository requires one. Report the missing review unless the user separately authorized submitting it and the account is eligible to do so.

## Verify the default branch

- Find the required default-branch run or checks tied to the resulting commit, not the superseded PR head.
- Wait for the repository's required post-merge signal. Treat skipped, cancelled, missing, or unrelated runs according to repository policy rather than as success.
- On failure, stop the queue and report the failing job, commit, and whether it appears caused by the merged change. Do not merge the next PR on stale pre-merge evidence.

## Refresh the remaining queue

After the default branch is verified:

- re-query each remaining PR's head, base branch and commit, mergeability, checks, reviews, threads, and timing gates;
- recompute ordering when merged dependencies, shared lockfiles, conflicts, or bot regeneration changed the queue;
- require a fresh exact-head decision for the next PR even when its SHA did not change, because its base and mergeability may have;
- treat a rebase, recreate request, or bot command as a separate external write.

The normal loop is one verified merge, one verified default-branch result, then one refreshed queue.

## Record the release disposition

Read the current release runbook and compare the merged default branch with the latest published version or artifact. Record one of:

- **release required**: repository policy or a distributable user-facing change requires a release;
- **release not justified**: the verified delta does not change the distributed product and policy does not require publication;
- **unresolved**: the published state, artifact delta, or release policy cannot be established.

A dependency or toolchain merge does not itself prove that a release is needed. Conversely, a dependency-only label does not prove that runtime behavior is unchanged. Inspect the actual distributed delta and policy.

Release disposition is analysis. Tagging, pushing, creating a GitHub Release, and publishing packages remain separate actions and separate completion claims.

## Final report

Report, separately:

- each PR's verified head and final lifecycle state;
- every external action actually performed;
- default-branch CI commit and result after each merge;
- refreshed blockers or changed ordering for remaining PRs;
- release disposition, evidence, and any unperformed release action.
