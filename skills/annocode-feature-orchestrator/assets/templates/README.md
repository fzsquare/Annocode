# {{TITLE}}

- Requirement-ID: {{REQUIREMENT_ID}}
- Created: {{CREATED_AT}}
- Status: INITIALIZED
- Current role: orchestrator
- Next role: planner

The parent Agent coordinates this workflow. Every functional role runs in a fresh context and communicates through handoff files. The workflow must pause for explicit user approval after Planner completion and again after Annotator completion.
