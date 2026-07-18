# Clean-Context Role Protocol

Requirement-ID: {{REQUIREMENT_ID}}

## Context isolation

Each role starts in a new Agent without parent conversation history. The initial prompt carries only Requirement-ID, Role, Task-ID when applicable, and Attempt. State is restored from files in this directory.

## Role ownership

- Orchestrator: MANIFEST.md, USER-APPROVALS.md, 70-final.md, summaries, approval requests, and routing only.
- Planner: 10-plan.md, 20-task-board.md, tasks, handoffs/01-planner-to-annotator.md.
- Annotator: source markers, 30-annotations.md, handoffs/02-annotator-to-orchestrator.md.
- Implementer: assigned Write set and one handoffs/implementers/<task>-<attempt>.md.
- Integration: 40-integration.md and handoffs/03-integration-to-test.md.
- Tester: 50-test-report.md and handoffs/04-test-to-acceptance.md.
- Acceptance: 60-acceptance.md and handoffs/05-acceptance-to-orchestrator.md.

## Handoff and approval rule

A downstream role starts only after its required upstream handoff has a complete status. In addition, Annotator requires an explicit user approval record for the matching Planner attempt, and Implementer requires an explicit user approval record for the matching Annotator attempt. Handoffs contain decisions and evidence, not hidden reasoning or chat summaries.

After Planner COMPLETE, Orchestrator must summarize the plan, set WAITING_FOR_PLANNER_APPROVAL, ask the user to confirm, and stop. After Annotator COMPLETE, Orchestrator must summarize annotations, set WAITING_FOR_ANNOTATOR_APPROVAL, ask the user to confirm, and stop. Approval must be explicit, recorded in USER-APPROVALS.md, and bound to the exact stage and attempt. Silence and unrelated replies are not approval.

## No role substitution

No Agent may perform another role to keep the workflow moving. If the required role cannot run, status becomes WAITING_FOR_MANUAL_AGENT.
