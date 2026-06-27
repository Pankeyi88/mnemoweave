## ADDED Requirements

### Requirement: Manual condense trigger
The system SHALL provide a `memory.py condense` subcommand that the agent can call to manually summarize the current buffer into a `segment` memory.

#### Scenario: Condense with intent
- **WHEN** agent runs `python memory.py condense --intent "Added sort feature to recall" --decisions "chose attrgetter over lambda"`
- **THEN** a segment memory is written with source `condense`, the provided intent as body, and decisions in frontmatter

#### Scenario: Condense emits open questions
- **WHEN** agent runs `python memory.py condense --open-questions "default sort order TBD"`
- **THEN** open_questions field appears in the segment frontmatter

#### Scenario: Condense clears buffer
- **WHEN** condense completes successfully
- **THEN** the event buffer is cleared

#### Scenario: Condense with empty buffer
- **WHEN** agent runs `python memory.py condense` but buffer is empty
- **THEN** the command prints "Buffer is empty, nothing to condense." and exits with code 0

### Requirement: Structured fields auto-populated on condense
When condense writes a segment memory, the system SHALL automatically populate `files_touched`, `entities`, `events_count`, and `created` from the buffer contents, without agent input.

#### Scenario: Auto-populate files and entities
- **WHEN** buffer contains events targeting `memory.py` and `memories_core.py` with entities `[MnemoWeave, Python]`
- **THEN** the segment frontmatter includes `files_touched: [memory.py, memories_core.py]` and `entities: [MnemoWeave, Python]`

### Requirement: Agent provides body text
The system SHALL accept a `--body` or positional argument for the segment body text. If not provided, the system SHALL auto-generate a structured summary from events.

#### Scenario: Body provided
- **WHEN** agent runs `condense` with `--body "Added sort feature"`
- **THEN** body is set to the provided text

#### Scenario: No body provided
- **WHEN** agent runs `condense` without `--body`
- **THEN** body is auto-generated as a list of events grouped by file
