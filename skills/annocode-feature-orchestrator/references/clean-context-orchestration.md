# Clean-Context Orchestration Protocol

## Core rule

The parent Agent coordinates but never performs planner, annotator, implementer, integration, tester, or acceptance work. Each role starts in a new context and restores state only from files under the user-specified requirement ID.

## Required identity

- Requirement-ID: user-provided, immutable and repository-unique.
- Role: planner, annotator, implementer, integration, tester, acceptance.
- Task-ID: required for implementers.
- Attempt: increments for retries or reassignments.

## Spawn contract

Use a fresh child without parent history. Send only:

    requirement_id: feature-example
    role: planner
    attempt: A1

The role Skill discovers its allowed inputs and outputs from PROTOCOL.md.

## Mandatory user approval checkpoints

After a Planner handoff reaches COMPLETE, the parent must summarize the requirement interpretation, acceptance criteria, task DAG, file ownership, risks, and open decisions. It then sets WAITING_FOR_PLANNER_APPROVAL and stops. Annotator may start only after the user explicitly approves that exact Planner attempt and the approval is recorded in USER-APPROVALS.md.

After an Annotator handoff reaches COMPLETE, the parent must summarize marker coverage, files and symbols, exemptions, blockers, and Implementer inputs. It then sets WAITING_FOR_ANNOTATOR_APPROVAL and stops. Implementers may start only after the user explicitly approves that exact Annotator attempt and the approval is recorded in USER-APPROVALS.md.

Approval never carries across attempts. Silence, unrelated replies, or awareness that a role completed are not approval. A requested revision creates a fresh attempt and requires a fresh summary and approval.

## Manual continuation

A manually created role Agent uses the same requirement ID. It writes the same handoff as an automatically created child. The parent can later continue by reading handoff status and the matching approval record. Manual role execution never bypasses the Planner or Annotator approval checkpoint.

## Failure routing

- Planning gap -> new Planner attempt.
- Annotation gap -> new Annotator attempt.
- Implementation defect -> new Implementer attempt for the affected task.
- Integration conflict -> affected Implementer task, not Integration coding.
- Test failure -> Acceptance classifies; Orchestrator routes to Implementer or Planner.
- Requirement ambiguity -> Acceptance BLOCKED and user decision.

## No fallback

If child-agent creation is unavailable, mark WAITING_FOR_MANUAL_AGENT. Never preserve apparent progress by doing role work in the parent context.
