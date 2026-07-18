# User Approval Audit Log

Requirement-ID: {{REQUIREMENT_ID}}

Append-only coordinator-owned log. Role Agents must not edit it. Never rewrite or delete an earlier decision; append a new entry for every approval, rejection, or requested revision.

## Entry format

### <UTC timestamp> — <PLANNER|ANNOTATOR> <attempt>

- Decision: APPROVED | REVISION_REQUESTED | REJECTED
- User confirmation text: <exact user-facing confirmation or decision text>
- Confirmed in task: <current Codex task/thread identifier when available>
- Recorded by: orchestrator
- Authorized next role: annotator | implementer | none
- Notes: <optional>

No approval has been recorded yet.
