## Why

MnemoWeave currently only writes memories when the agent explicitly calls `memorize`, typically once per completed task. This means intermediate decisions, discoveries, dead ends, file modifications, and entity interactions are lost between manual memory writes. As sessions grow longer, the ratio of "useful durable context" to "memories written" becomes unacceptably low, weakening the value of recall and preview.

## What Changes

- Add an **event buffer** that automatically captures structured snapshots of tool calls (reads, writes, edits, searches, runs) with extracted entities and file targets
- Add a **condense** mechanism: agent manually triggers summarization of the buffer into a high-quality `segment` memory with semantic context
- Add an **auto-flush** mechanism: system automatically writes a structured `segment` memory when the buffer exceeds a count or time threshold
- Introduce a new memory type `segment` with additional fields: `source` (condense|auto_flush), `files_touched`, `events_count`, and optional `decisions`/`open_questions`
- Agent can optionally write a `session_digest` at session end for a top-level overview
- All buffer processing is pure Python — zero additional LLM token cost for capture and auto-flush; minimal cost for agent-supervised condense

## Capabilities

### New Capabilities
- `buffer-capture`: automatic structured event capture from tool call context, with entity extraction and dedup
- `buffer-condense`: agent-triggered summarization of buffer events into a semantic `segment` memory
- `buffer-auto-flush`: system-triggered emission of `segment` memory when buffer exceeds count (15) or time (20min) thresholds
- `segment-memory`: new memory type `segment` with extended frontmatter (`source`, `files_touched`, `events_count`, `decisions`, `open_questions`)
- `session-digest`: optional end-of-session summary memory that references segment memories

### Modified Capabilities
- (none — no existing specs to modify)

## Impact

- `scripts/memories_core.py`: new module(s) for event buffer data structures, append/lookup, condenser, auto-flush logic
- `scripts/memory.py`: new CLI subcommands (`buffer`, `condense`) and optional `--digest` flag
- `SKILL.md`: updated "When To Use" section with buffer, condense, and digest guidelines
- No changes to existing memory read paths (preview, recall) — `segment` type is backward-compatible
- No new runtime dependencies — Python standard library only
