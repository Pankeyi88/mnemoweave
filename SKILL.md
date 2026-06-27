---
name: mnemoweave
description: MnemoWeave is an agent-agnostic persistent memory weave. Memorize observations, recall past context, and preview recent activity. Memories are stored as Markdown files in a configurable memory root.
---

# MnemoWeave

MnemoWeave is an agent-agnostic persistent memory weave. It stores each memory as a standalone Markdown file with YAML frontmatter and a natural-language Markdown body.

This skill is self-contained in `C:\Users\sypky\.agents\skills\mnemoweave\`. Agents that do not understand Codex skills can discover the machine-readable manifest at `mnemoweave.json` and call the Python CLI at `scripts\memory.py`.

## Preferred Entry Point

Use `scripts\memory.py` for all operations. The only required runtime is `python`.

### Storage Resolution

Memory root resolution order:

1. CLI `--root`
2. Environment variable `AGENT_MEMORY_ROOT`
3. `mnemoweave.json` field `memory_root`
4. Fallback `E:\_memories`

Project scope resolution order:

1. CLI `--project`
2. Environment variable `AGENT_MEMORY_PROJECT`
3. No project scope

When no project scope is set, preview and recall include all memories. When a project scope is set, preview and recall only include memories with matching `project` frontmatter.

## Commands

### Preview recent context

```bash
python scripts\memory.py preview
```

```bash
python scripts\memory.py --root D:\memories --project demo-vault preview --days 30
```

### Recall memories

```bash
python scripts\memory.py recall --query "CUDA"
```

```bash
python scripts\memory.py --project demo-vault recall --entity "PyTorch"
```

```bash
python scripts\memory.py --project demo-vault recall --query "experiment" --entity "CUDA" --limit 20
```

`recall` returns a JSON array with file path, frontmatter fields, project, and body preview. Results are sorted newest-first.

### Memorize durable context

```bash
python scripts\memory.py memorize --type task_complete --agent codex --entities PyTorch CUDA --summary "Completed time series experiment" --body "Ran LSTM time series experiment using PyTorch with CUDA acceleration."
```

```bash
python scripts\memory.py --project demo-vault memorize --type task_complete --agent codex --entities Python MnemoWeave --summary "Updated memory system" --body "Added configurable storage and project scoping."
```

`memorize` always appends a new file. It never overwrites existing memories.

### Event Buffer

Buffer events as they happen, then flush them into segment memories.

```bash
python scripts\memory.py buffer append --event-type file_edit --summary "Modified core module" --file "scripts/core.py" --entity "Python"
```

```bash
python scripts\memory.py buffer status
```

### Condense

Condense the buffer into a segment memory and clear the buffer.

```bash
python scripts\memory.py condense --agent opencode --intent "Implemented buffer system"
```

```bash
python scripts\memory.py condense --agent opencode --intent "Quick note" --body "Custom body content"
```

### Session Digest

Write a session digest referencing segment memories from the current session.

```bash
python scripts\memory.py digest --agent opencode --summary "Morning coding session"
```

### Auto-Flush

Automatically flush the buffer if count or time thresholds are met. Deduplicates against recent memories using Jaccard similarity.

```bash
python scripts\memory.py auto-flush --agent opencode
```

## When To Use

### preview

- Run at agent startup when possible.
- Run when a recent context snapshot would help orient the session.

### recall

Call recall when the user's request:

- Mentions previous work, last time, continuing, or backtracking.
- Involves known entities, tools, libraries, projects, or workflows.
- Needs historical context, durable preferences, or cross-agent context.

No recall is needed for generic context-independent questions.

### memorize

Write a memory after:

- Completing a task that produced useful durable information.
- Discovering a stable user preference, workflow detail, or tool choice.
- Creating or modifying a notable note, artifact, or project convention.

### buffer

Use `buffer append` when you want to capture granular events during a session without writing full memories. Good for file edits, command runs, and other micro-actions.

### condense

Use `condense` when the buffer is ready to be processed into a proper segment memory. Useful when you have many small events that should be grouped together.

### digest

Use `digest` at the end of a session to create a summary referencing all segment memories created during the session.

### auto-flush

Use `auto-flush` to automatically check buffer thresholds and create a segment memory if triggered. Deduplicates against recent memories using Jaccard similarity to avoid redundant writes.

## Storage

- Default location: `E:\_memories\`
- Override location: `--root` or `AGENT_MEMORY_ROOT`
- Optional project scope: `--project` or `AGENT_MEMORY_PROJECT`
- File format: standalone `.md` files with YAML frontmatter and Markdown body.
- Filename format: `YYYY-MM-DD-NNN.md`
- Frontmatter fields: `type`, `agent`, `summary`, `created`, `entities`; optional `project`, `source`, `files_touched`, `events_count`, `decisions`, `open_questions`

## Implementation

- CLI entrypoint: `scripts\memory.py`
- Core module: `scripts\memories_core.py`
- Manifest: `mnemoweave.json`
- Runtime: Python standard library only
