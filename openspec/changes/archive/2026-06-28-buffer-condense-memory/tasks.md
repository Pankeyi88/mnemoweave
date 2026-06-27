## 1. Event Buffer Core

- [x] 1.1 Add `BufferEvent` dataclass and `EventBuffer` class to `memories_core.py`
- [x] 1.2 Implement `buffer_append()` with auto-flush check (count + time)
- [x] 1.3 Implement heuristic entity extraction from file paths and known entity list
- [x] 1.4 Implement `buffer_status()` for debug output

## 2. Segment Memory

- [x] 2.1 Add `write_segment()` function that creates segment-type memory with extended frontmatter (`source`, `files_touched`, `events_count`, optional `decisions`/`open_questions`)
- [x] 2.2 Verify backward compatibility: `parse_memory()` handles new frontmatter fields without errors
- [x] 2.3 Verify segment memories appear correctly in `preview` and `recall`

## 3. Auto-Flush

- [x] 3.1 Implement count-based auto-flush trigger (default: 15 events)
- [x] 3.2 Implement time-based auto-flush trigger (default: 20 minutes)
- [x] 3.3 Implement dedup logic: skip flush if Jaccard similarity > 0.7 with last auto-flush
- [x] 3.4 Auto-flush writes structured-only segment (no decisions/open_questions)
- [x] 3.5 Auto-flush does NOT clear the buffer

## 4. Condense CLI

- [x] 4.1 Add `memory.py condense` subcommand with `--intent`, `--body`, `--decisions`, `--open-questions` flags
- [x] 4.2 Condense auto-populates `files_touched`, `entities`, `events_count` from buffer
- [x] 4.3 Condense auto-generates body from events if `--body` not provided
- [x] 4.4 Condense clears the buffer after successful write
- [x] 4.5 Handle empty buffer case gracefully

## 5. Buffer CLI

- [x] 5.1 Add `memory.py buffer status` subcommand
- [x] 5.2 Output: event count, oldest timestamp, remaining count/age to next flush

## 6. Session Digest

- [x] 6.1 Add `memory.py digest` subcommand with `--summary` flag
- [x] 6.2 Digest references segment memories from current session in body
- [x] 6.3 Digest writes `type: session_digest` with `segment_count` and union entities
- [x] 6.4 Handle case with no segment memories gracefully

## 7. Documentation

- [x] 7.1 Update SKILL.md "When To Use" section with buffer, condense, and digest guidelines
- [x] 7.2 Update CLI examples in SKILL.md to include new subcommands
- [x] 7.3 Validate all new commands work end-to-end with a manual test session
