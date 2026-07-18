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

## Manual continuation

A manually created role Agent uses the same requirement ID. It writes the same handoff as an automatically created child. The parent can later continue by reading handoff status.

## Failure routing

- Planning gap -> new Planner attempt.
- Annotation gap -> new Annotator attempt.
- Implementation defect -> new Implementer attempt for the affected task.
- Integration conflict -> affected Implementer task, not Integration coding.
- Test failure -> Acceptance classifies; Orchestrator routes to Implementer or Planner.
- Requirement ambiguity -> Acceptance BLOCKED and user decision.

## No fallback

If child-agent creation is unavailable, mark WAITING_FOR_MANUAL_AGENT. Never preserve apparent progress by doing role work in the parent context.
