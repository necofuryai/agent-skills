# Ledger contract

Read this when persisting or reconciling an inventory, performing moves, or resuming a migration. Adapt the existing task's format when it can represent these distinctions; preserve existing records and add missing fields rather than replacing its schema unnecessarily.

## Run record

Store these facts in the task workspace, not the installed skill:

- Account/workspace identity sufficient to distinguish the target, without credentials.
- Requested scope and the existing instruction authorizing execution, if any.
- Project IDs with observed names, purposes, and relevant sharing scope.
- Enumeration coverage: `complete`, `partial`, or `unknown`; the last observed boundary/cursor and its timestamp. `complete` means an authoritative full list or the actual end of the requested listing was reached, not merely that scrolling stopped producing results.
- Run state (`running`, `paused`, `blocked`, `completed`), current operation, pending conversation IDs, unresolved items, and the next step.
- Start time and baseline counts for this invocation, so cumulative migration outcomes and newly attempted moves can be distinguished from confirmations recovered after a resume.

## Conversation record

Use stable IDs as keys. A canonical conversation URL can serve as the key when no separate ID is exposed. Titles are labels and may collide or change.

| Field | Meaning |
| --- | --- |
| `conversation_id`, `url`, `title` | Identity and observed display label. |
| `source_project_id` | Membership observed before this attempt; null only for confirmed unfiled membership. Use a separate unknown state when membership is inaccessible. |
| `target_project_id` | Intended destination; null for an explicitly retained unfiled item or unresolved classification, distinguished by status. |
| `classification_reason` | Decision and the title/content/Project purpose supporting it, or the precise unresolved question. |
| `status` | Exactly one of the current outcomes below. |
| `observed_project_id`, `observed_at` | Last verified membership and timestamp; omit unknown membership rather than implying unfiled. |
| `evidence` | The read that established membership: source type, ID/link, and concise observation or saved reference. Avoid copying full conversation bodies. |
| `attempts` | Source, destination, attempt time, observed outcome/error, and subsequent verification or correction. Preserve this history. |

## Current outcomes

| Status | Interpretation |
| --- | --- |
| `pending` | Classified and awaiting execution. |
| `moved_verified` | A read verified intended membership after a recorded move attempt, including delayed confirmation of an earlier attempt. Preserve when the attempt and verification each occurred. |
| `already_correct` | A current read found the intended membership and this migration has no move attempt for that item; not a newly moved item. |
| `retained` | Leaving the item in place is supported by the user's scope or accepted classification policy. |
| `needs_decision` | Destination, requested disposition, or membership discrepancy needs resolution. |
| `inaccessible` | Required content or membership cannot be inspected. |
| `failed` | The attempt failed and a read confirmed the intended move did not take effect. |
| `unverified` | An attempt was started or may have occurred, but its effect has not been established. |

An error response with no membership read is `unverified`, not evidence that nothing moved. A changed membership invalidates the old current outcome but does not erase its history. Persist updates after each verified move and at every pause/blocker; replace snapshot files atomically where supported. Reconcile a saved `unverified` attempt before issuing it again.

## Reconciliation and completion

Compute counts from unique current records, not accumulated UI counters or attempt totals:

```text
observed_unique = pending + moved_verified + already_correct + retained
                + needs_decision + inaccessible + failed + unverified
```

This equality checks accounting only. Also compare the in-scope expected ID-to-destination mapping with observed membership. A count match with different IDs or wrong destinations is a discrepancy. Include pre-existing Project members only when the requested scope covers them.

For duplicate titles, preserve each distinct ID. For duplicate observations of the same ID, reconcile one current record and preserve relevant attempt history. If a previously counted item is now missing or changed, record the discrepancy and remove it from the current verified total until resolved.

Full migration completion requires complete requested enumeration, resolved in-scope membership checks, no pending or unresolved outcome, and user acceptance of any retained disposition. For a partial run, report the observed denominator and coverage limit, never a fabricated total for the entire account.

The final report should identify the run record and include cumulative verified outcomes plus this invocation's newly attempted-and-confirmed moves, recovered confirmations of earlier attempts, already-correct, retained, and unresolved counts; unresolved IDs/links and reasons; and the next action. Recovered confirmations do not count as newly executed moves. Keep an explicit pause distinct from a transient operational block so an audit or status request cannot accidentally resume a user-paused migration.
