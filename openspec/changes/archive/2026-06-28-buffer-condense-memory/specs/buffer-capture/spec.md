## ADDED Requirements

### Requirement: Automatic event capture
The system SHALL automatically capture a structured event after each agent tool call. Each event SHALL record the tool call type, target, extracted entities, and result summary.

#### Scenario: Capture read event
- **WHEN** agent reads a file `memory.py`
- **THEN** a BufferEvent with type `read`, target `memory.py`, and extracted entities is appended to the buffer

#### Scenario: Capture edit event
- **WHEN** agent edits `memories_core.py` with diff summary "added sort_by parameter"
- **THEN** a BufferEvent with type `edit`, target `memories_core.py`, and diff_summary is appended

#### Scenario: Capture search event
- **WHEN** agent executes a search query "python sort dataclass by field"
- **THEN** a BufferEvent with type `search`, target containing the query, and result summary is appended

#### Scenario: Capture run event
- **WHEN** agent runs a shell command `pytest tests/ -v`
- **THEN** a BufferEvent with type `run`, target containing the command, and exit status/output is appended

### Requirement: Heuristic entity extraction
The system SHALL extract entities from each event using simple heuristic matching against known entity names and file path stems. This extraction SHALL involve zero LLM calls.

#### Scenario: Extract from file path
- **WHEN** target is `memory.py`
- **THEN** the system extracts "memory" and "memory.py" as candidate entities

#### Scenario: Extract from known entity list
- **WHEN** target contains text matching a previously seen entity like "MnemoWeave"
- **THEN** the matching entity is included in entities_found

### Requirement: Buffer append is non-blocking
The `append()` call SHALL complete in O(1) time and SHALL NOT raise exceptions under normal operation.

#### Scenario: Normal append
- **WHEN** append is called with a valid BufferEvent
- **THEN** the event is added to the deque without error

#### Scenario: Buffer at max capacity
- **WHEN** buffer has 100 events and a new event is appended
- **THEN** the oldest event is silently discarded and the new event is appended

### Requirement: CLI buffer status subcommand
The system SHALL provide a `memory.py buffer status` subcommand that prints current buffer size, oldest event age, and next auto-flush trigger.

#### Scenario: Buffer status output
- **WHEN** user runs `python memory.py buffer status`
- **THEN** output shows count, oldest timestamp, and remaining count/age to next flush
