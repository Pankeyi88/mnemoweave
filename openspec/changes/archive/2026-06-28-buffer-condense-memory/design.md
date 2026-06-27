## Context

MnemoWeave currently stores memories only when the agent explicitly calls `memorize`, producing a single `task_complete` or `observation` entry per manual trigger. There is no automatic capture of intermediate tool calls, file modifications, entity discoveries, or decisions made during a session. The existing `Memory` dataclass and `write_memory()` function in `memories_core.py` are simple and well-factored — they accept structured fields and write a Markdown file with YAML frontmatter. The CLI entrypoint in `memory.py` uses argparse with subcommands.

This design extends the existing architecture with an in-memory event buffer that requires no runtime dependencies beyond Python standard library.

## Goals / Non-Goals

**Goals:**

- Automatically capture structured events (read, write, edit, search, run) from agent tool calls without LLM involvement
- Provide an agent-triggered `condense` mechanism that summarizes buffer events into a semantic `segment` memory
- Provide a system-triggered `auto-flush` that writes a structured `segment` memory when buffer exceeds count (15) or time (20min) thresholds
- Introduce a new `segment` memory type with extended frontmatter: `source`, `files_touched`, `events_count`, optional `decisions`/`open_questions`
- Optionally support an end-of-session `session_digest` that references segment-level memories
- Keep all buffer processing in pure Python — zero LLM cost for capture and auto-flush

**Non-Goals:**

- No changes to existing `preview` or `recall` commands (segment type is backward-compatible)
- No persistent buffer storage across sessions (buffer is in-memory, lost on agent restart)
- No automatic semantic understanding of event content (entity extraction is heuristic via simple string matching against known entities)

## Decisions

| Decision | Choice | Rationale | Alternatives Considered |
|---|---|---|---|
| Buffer storage | In-memory `deque[BufferEvent]` | Simple, zero persistence overhead, matches agent session lifecycle. Buffer loss on restart is acceptable because condense/flush capture what matters. | SQLite, JSONL log file — added complexity without clear benefit for ephemeral buffer |
| Entity extraction | Heuristic: substring match against known entity list + file path stem parsing | Zero LLM cost, good enough for recall. Agent can enrich entities during condense. | LLM-based extraction — accurate but costly; regex patterns — too brittle |
| Auto-flush triggers | `count >= 15` OR `age >= 20min` (both configurable) | Covers both intensive tool sessions and sparse thinking sessions. Conservative defaults to avoid noise. | Single trigger — misses either high-frequency or low-frequency sessions |
| Condense output | Agent writes intent/decision text; system fills structured fields | Divides labor: agent supplies "why" (zero cost), system supplies "what" (zero cost). | Pure agent summary — agent must remember everything; pure system summary — lacks semantic depth |
| Auto-flush dedup | Skip flush if buffer events overlap heavily with last flush | Prevents redundant identical segment memories. Overlap measured by file + entity Jaccard similarity. | Always flush — flood of duplicates; merge into existing segment — more complex |
| Segment frontmatter | Add `source`, `files_touched`, `events_count`, optional `decisions`, `open_questions` | Backward-compatible: new fields are additive, existing readers ignore unknown frontmatter. | New file format — unnecessary breakage; embed in body — harder to query with frontmatter-aware tools |
| CLI interface | New subcommands `buffer` and `condense` under existing `memory.py` | Consistent with current CLI design. `memory.py buffer` for status/debug, `memory.py condense` for manual summarization. | Separate script — fragmented; modify `memorize` — overloads existing command semantics |

## Architecture

```
Agent Session
    │
    ▼
┌─────────────────────────────────────┐
│         Event Buffer                │
│  (in-memory deque[BufferEvent])     │
│                                     │
│  append()    ←─ called by agent     │
│                after each tool call │
└─────────┬───────────────────────────┘
          │
          ├── auto_flush check ──▶  count ≥ 15  OR  age ≥ 20min
          │                           │
          │                           ▼
          │                    ┌──────────────┐
          │                    │ auto_flush() │ ──▶ segment memory (source: auto_flush)
          │                    └──────────────┘
          │
          ├── agent calls condense ──▶  agent provides intent + decisions
          │                           │
          │                           ▼
          │                    ┌──────────────┐
          │                    │ condense()   │ ──▶ segment memory (source: condense)
          │                    └──────────────┘
          │
          └── session_end ──▶  optional digest()
                               ──▶ session_digest memory
```

## Data Structures

```python
@dataclass
class BufferEvent:
    ts: str                      # ISO timestamp
    type: Literal["read", "write", "edit", "search", "run"]
    target: str                  # file path or URL or search query
    entities_found: list[str]    # heuristic extraction
    diff_summary: str | None     # for edit events, brief diff description
    result: str | None           # for search/run events

@dataclass
class EventBuffer:
    events: deque[BufferEvent]
    max_events: int = 100
    auto_flush_count: int = 15
    auto_flush_interval_min: int = 20
    last_flush_at: datetime | None = None
```

## Segment Memory Format

```markdown
---
type: segment
agent: codex
project: mnemoweave
created: 2026-06-27T14:05:30+08:00
source: condense              # or "auto_flush"
entities:
  - MnemoWeave
  - recall
  - sort
files_touched:
  - memories_core.py
  - memory.py
events_count: 9
decisions:                    # only in condense
  - "chose sorted() with attrgetter over custom comparison"
open_questions:               # only in condense
  - "should --sort default to 'created' or 'relevance'?"
---
# agent-written or auto-generated summary
```

## Risks / Trade-offs

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Auto-flush writes too many low-value memories | Medium | Medium | Conservative defaults (15/20min); dedup by file/entity overlap; user-configurable thresholds |
| Condense relies on agent remembering to call it | Medium | Low | Auto-flush acts as safety net; digest at session end catches anything missed |
| Entity heuristic misses important entities | Medium | Low | Entities can be manually added during condense; false negatives are recoverable |
| In-memory buffer lost on agent crash | Low | Low | Auto-flush fires frequently enough that most events are captured before crash; recovery is restart + preview from segment memories |
