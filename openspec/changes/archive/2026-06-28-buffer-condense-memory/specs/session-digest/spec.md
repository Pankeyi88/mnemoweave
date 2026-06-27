## ADDED Requirements

### Requirement: Optional end-of-session digest
The system SHALL provide an optional `memory.py digest` subcommand that writes a `session_digest` memory summarizing the entire session. This command SHALL reference segment memories written during the session.

#### Scenario: Write session digest
- **WHEN** agent runs `python memory.py digest --summary "Refactored memory system"`
- **THEN** a memory file with `type: session_digest` is written

#### Scenario: Digest includes segment references
- **WHEN** digest is written and segment memories exist from this session
- **THEN** body includes a list of segment filenames and their summaries

#### Scenario: No segments to reference
- **WHEN** digest is written but no segment memories exist from this session
- **THEN** body indicates "No segment-level memories recorded this session"

### Requirement: Session digest frontmatter
A session_digest memory SHALL support these frontmatter fields:

| Field | Required | Description |
|---|---|---|
| `type` | yes | `session_digest` |
| `agent` | yes | passed by caller |
| `created` | yes | ISO timestamp |
| `entities` | yes | union of entities across all session segments |
| `session_start` | no | timestamp of session start |
| `segment_count` | yes | number of segment memories written this session |

#### Scenario: Valid digest frontmatter
- **WHEN** a session_digest is written
- **THEN** the file has valid YAML frontmatter with at minimum: type, agent, created, entities, segment_count

### Requirement: Digest is optional
The digest SHALL NOT be written automatically. It SHALL only be written when explicitly invoked by the agent.

#### Scenario: No automatic digest
- **WHEN** a session ends (agent terminates)
- **THEN** no digest is written unless the agent explicitly called the digest command
