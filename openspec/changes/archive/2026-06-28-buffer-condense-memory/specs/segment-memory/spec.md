## ADDED Requirements

### Requirement: New memory type `segment`
The system SHALL support a new memory type `segment` in addition to existing `observation` and `task_complete`. Segment memories represent a condensed summary of a contiguous block of agent work.

#### Scenario: Write segment via condense
- **WHEN** agent calls `memory.py condense`
- **THEN** a `.md` file with `type: segment` in frontmatter is written to the memory root

#### Scenario: Write segment via auto-flush
- **WHEN** auto-flush triggers
- **THEN** a `.md` file with `type: segment` and `source: auto_flush` is written

#### Scenario: Segment appears in preview
- **WHEN** user runs `memory.py preview`
- **THEN** segment memories are listed alongside observation and task_complete memories

#### Scenario: Segment appears in recall
- **WHEN** user runs `memory.py recall --query sort`
- **THEN** segment memories matching the query are returned in results

### Requirement: Segment frontmatter fields
A segment memory SHALL support these frontmatter fields:

| Field | Required | Source |
|---|---|---|
| `type` | yes | `segment` (fixed) |
| `agent` | yes | passed by caller |
| `created` | yes | ISO timestamp |
| `source` | yes | `condense` or `auto_flush` |
| `entities` | yes | extracted from buffer |
| `files_touched` | yes | auto-populated from buffer targets |
| `events_count` | yes | count of events condensed |
| `project` | no | inherited from CLI/project scope |
| `decisions` | no | agent-provided (condense only) |
| `open_questions` | no | agent-provided (condense only) |

#### Scenario: Valid segment frontmatter
- **WHEN** a segment memory is written
- **THEN** the file has valid YAML frontmatter with at minimum: type, agent, created, source, entities, files_touched, events_count

#### Scenario: Optional fields absent in auto_flush
- **WHEN** source is `auto_flush`
- **THEN** decisions and open_questions are NOT present in frontmatter

### Requirement: Backward compatibility
Existing code that reads memory files SHALL continue to work with segment-type memories. Unknown frontmatter fields SHALL be ignored.

#### Scenario: Parse segment in existing code
- **WHEN** `parse_memory()` reads a segment file
- **THEN** it returns a valid Memory dataclass with type="segment" and any frontmatter fields accessible

#### Scenario: Unknown fields ignored
- **WHEN** `parse_memory()` encounters `files_touched` or `source` fields
- **THEN** they are stored in the generic fields dict and do not cause parse errors

### Requirement: Filename format
Segment memories SHALL use the same filename format as existing memories: `YYYY-MM-DD-NNN.md`, using the same `next_filename()` counter.

#### Scenario: Same counter
- **WHEN** a segment and a task_complete are written on the same day
- **THEN** they share the same sequential counter without collision
