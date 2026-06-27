## ADDED Requirements

### Requirement: Count-based auto-flush
The system SHALL automatically write a `segment` memory when the event buffer reaches a configurable count threshold (default: 15 events).

#### Scenario: Buffer reaches threshold
- **WHEN** the 15th BufferEvent is appended
- **THEN** an auto-flush is triggered and a segment memory with `source: auto_flush` is written

#### Scenario: Configurable threshold
- **WHEN** `auto_flush_count` is set to 10
- **THEN** flush triggers at 10 events instead of 15

#### Scenario: Count-based flush does not clear buffer
- **WHEN** auto-flush fires due to count threshold
- **THEN** the buffer is NOT cleared (events remain for subsequent manual condense)

### Requirement: Time-based auto-flush
The system SHALL automatically write a `segment` memory when the oldest event in the buffer exceeds a configurable age threshold (default: 20 minutes).

#### Scenario: Buffer ages past threshold
- **WHEN** 20 minutes have passed since the oldest event in the buffer
- **THEN** an auto-flush is triggered and a segment memory is written

#### Scenario: Configurable interval
- **WHEN** `auto_flush_interval_min` is set to 30
- **THEN** flush triggers at 30 minutes instead of 20

#### Scenario: Time-based flush does not clear buffer
- **WHEN** auto-flush fires due to time threshold
- **THEN** the buffer is NOT cleared

### Requirement: Dedup before auto-flush
Before writing an auto-flush segment, the system SHALL compare the current buffer's file/entity profile against the last auto-flush segment written. If the Jaccard similarity exceeds 0.7, the flush SHALL be skipped.

#### Scenario: Similar content skipped
- **WHEN** current buffer events touch the same files as the last auto-flush segment
- **THEN** the flush is skipped and no new segment is written

#### Scenario: New content flushes
- **WHEN** current buffer events involve files not in the last auto-flush segment
- **THEN** the flush proceeds normally

### Requirement: Auto-flush emits structured-only content
Auto-flush segments SHALL contain only structured fields (files_touched, entities, events_count) and an auto-generated body listing event summaries. They SHALL NOT contain `decisions` or `open_questions`.

#### Scenario: Auto-flush body format
- **WHEN** auto-flush writes a segment memory
- **THEN** body contains a grouped list of events by file, with no natural language narrative
