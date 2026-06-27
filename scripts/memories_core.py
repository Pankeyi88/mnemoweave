from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable
import json
import os

DEFAULT_MEMORIES_ROOT = Path(r"E:\_memories")

DEFAULT_FLUSH_COUNT = 15
DEFAULT_FLUSH_MINUTES = 20
DEFAULT_JACCARD_THRESHOLD = 0.7

BUFFER_FILE = "_buffer.json"


@dataclass(frozen=True)
class Memory:
    path: Path
    filename: str
    type: str | None
    agent: str | None
    summary: str | None
    created: str | None
    project: str | None
    entities: list[str]
    body: str
    source: str | None = None
    files_touched: list[str] = field(default_factory=list)
    events_count: int | None = None
    decisions: list[str] | None = None
    open_questions: list[str] | None = None


@dataclass
class BufferEvent:
    timestamp: str
    event_type: str
    summary: str
    file_path: str | None = None
    entity: str | None = None


@dataclass
class EventBuffer:
    root: Path
    project: str | None = None
    flush_count: int = DEFAULT_FLUSH_COUNT
    flush_minutes: int = DEFAULT_FLUSH_MINUTES
    _events: list[BufferEvent] = field(default_factory=list, repr=False)
    _last_flush: datetime | None = field(default=None, repr=False)

    @property
    def _buffer_path(self) -> Path:
        return self.root / BUFFER_FILE

    def _load(self) -> None:
        if self._buffer_path.exists():
            try:
                data = json.loads(self._buffer_path.read_text(encoding="utf-8"))
                self._events = [
                    BufferEvent(**e) for e in data.get("events", [])
                ]
                self._last_flush = (
                    datetime.fromisoformat(data["last_flush"])
                    if data.get("last_flush")
                    else None
                )
            except (json.JSONDecodeError, KeyError, TypeError):
                self._events = []
                self._last_flush = None

    def _save(self) -> None:
        self._buffer_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "events": [
                {
                    "timestamp": e.timestamp,
                    "event_type": e.event_type,
                    "summary": e.summary,
                    "file_path": e.file_path,
                    "entity": e.entity,
                }
                for e in self._events
            ],
            "last_flush": self._last_flush.isoformat() if self._last_flush else None,
        }
        self._buffer_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def buffer_append(
        self,
        event_type: str,
        summary: str,
        file_path: str | None = None,
        entity: str | None = None,
    ) -> BufferEvent:
        self._load()
        event = BufferEvent(
            timestamp=datetime.now().astimezone().isoformat(),
            event_type=event_type,
            summary=summary,
            file_path=file_path,
            entity=entity,
        )
        self._events.append(event)
        self._save()
        return event

    def buffer_status(self) -> dict:
        self._load()
        now = datetime.now().astimezone()
        oldest = None
        if self._events:
            oldest = datetime.fromisoformat(self._events[0].timestamp)

        age_to_flush = None
        count_to_flush = max(0, self.flush_count - len(self._events))
        if oldest:
            elapsed_minutes = (now - oldest).total_seconds() / 60
            age_to_flush = max(0.0, self.flush_minutes - elapsed_minutes)

        return {
            "event_count": len(self._events),
            "oldest_timestamp": oldest.isoformat() if oldest else None,
            "count_to_flush": count_to_flush,
            "age_to_flush_minutes": round(age_to_flush, 1) if age_to_flush is not None else None,
            "last_flush": self._last_flush.isoformat() if self._last_flush else None,
        }

    def should_flush(self) -> bool:
        self._load()
        if not self._events:
            return False
        if len(self._events) >= self.flush_count:
            return True
        if self._events:
            oldest = datetime.fromisoformat(self._events[0].timestamp)
            now = datetime.now().astimezone()
            if (now - oldest).total_seconds() / 60 >= self.flush_minutes:
                return True
        return False

    def clear(self) -> None:
        self._events = []
        self._last_flush = None
        self._save()

    @property
    def events(self) -> list[BufferEvent]:
        self._load()
        return list(self._events)


KNOWN_ENTITIES = [
    "Python", "MnemoWeave", "OpenSpec", "Node.js", "TypeScript",
    "Docker", "Kubernetes", "PyTorch", "TensorFlow", "CUDA",
    "Git", "GitHub", "VS Code", "Redis", "PostgreSQL",
    "FastAPI", "Flask", "Django", "React", "Vue",
]


def extract_entities_from_file(file_path: str, known: list[str] | None = None) -> list[str]:
    entities: list[str] = []
    path_lower = file_path.lower()
    known_list = known or KNOWN_ENTITIES
    for name in known_list:
        if name.lower() in path_lower:
            entities.append(name)
    return entities


def ensure_memories_dir(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)


def next_filename(root: Path, now: datetime | None = None) -> str:
    ensure_memories_dir(root)
    current = now or datetime.now().astimezone()
    today = current.strftime("%Y-%m-%d")
    max_number = 0
    for path in root.glob(f"{today}-*.md"):
        suffix = path.stem.removeprefix(f"{today}-")
        if suffix.isdigit():
            max_number = max(max_number, int(suffix))
    return f"{today}-{max_number + 1:03d}.md"


def write_memory(
    *,
    root: Path,
    memory_type: str,
    agent: str,
    entities: Iterable[str],
    summary: str,
    body: str,
    project: str | None = None,
    source: str | None = None,
    files_touched: list[str] | None = None,
    events_count: int | None = None,
    decisions: list[str] | None = None,
    open_questions: list[str] | None = None,
) -> Path:
    ensure_memories_dir(root)
    path = root / next_filename(root)
    created = datetime.now().astimezone().isoformat()
    entity_list = [e for e in entities if e]
    entity_lines = "\n".join(f"  - {entity}" for entity in entity_list)
    project_line = f"project: {project}\n" if project else ""
    source_line = f"source: {source}\n" if source else ""
    files_lines = ""
    if files_touched:
        files_lines = "files_touched:\n" + "\n".join(f"  - {f}" for f in files_touched) + "\n"
    events_line = f"events_count: {events_count}\n" if events_count is not None else ""
    decisions_lines = ""
    if decisions:
        decisions_lines = "decisions:\n" + "\n".join(f"  - {d}" for d in decisions) + "\n"
    open_q_lines = ""
    if open_questions:
        open_q_lines = "open_questions:\n" + "\n".join(f"  - {q}" for q in open_questions) + "\n"

    content = (
        "---\n"
        f"type: {memory_type}\n"
        f"agent: {agent}\n"
        f"summary: {summary}\n"
        f"created: {created}\n"
        f"{project_line}"
        f"{source_line}"
        f"{files_lines}"
        f"{events_line}"
        f"{decisions_lines}"
        f"{open_q_lines}"
        "entities:\n"
        f"{entity_lines}\n"
        "---\n"
        f"{body.strip()}\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def write_segment(
    *,
    root: Path,
    agent: str,
    summary: str,
    body: str,
    source: str = "auto-flush",
    files_touched: list[str] | None = None,
    entities: Iterable[str] | None = None,
    events_count: int = 0,
    decisions: list[str] | None = None,
    open_questions: list[str] | None = None,
    project: str | None = None,
) -> Path:
    return write_memory(
        root=root,
        memory_type="segment",
        agent=agent,
        entities=entities or [],
        summary=summary,
        body=body,
        project=project,
        source=source,
        files_touched=files_touched,
        events_count=events_count,
        decisions=decisions,
        open_questions=open_questions,
    )


def parse_memory(path: Path) -> Memory | None:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except OSError:
        return None

    if not content.startswith("---"):
        return None

    end_frontmatter = content.find("---", 3)
    if end_frontmatter < 0:
        return None

    frontmatter = content[3:end_frontmatter].strip()
    body = content[end_frontmatter + 3 :].strip()
    fields: dict[str, str] = {}
    entities: list[str] = []
    files_touched: list[str] = []
    decisions: list[str] = []
    open_questions: list[str] = []
    current_key: str | None = None

    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("-") and current_key == "entities":
            entities.append(stripped[1:].strip())
            continue
        if stripped.startswith("-") and current_key == "files_touched":
            files_touched.append(stripped[1:].strip())
            continue
        if stripped.startswith("-") and current_key == "decisions":
            decisions.append(stripped[1:].strip())
            continue
        if stripped.startswith("-") and current_key == "open_questions":
            open_questions.append(stripped[1:].strip())
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            fields[current_key] = value.strip()

    return Memory(
        path=path,
        filename=path.name,
        type=fields.get("type"),
        agent=fields.get("agent"),
        summary=fields.get("summary"),
        created=fields.get("created"),
        project=fields.get("project"),
        entities=entities,
        body=body,
        source=fields.get("source"),
        files_touched=files_touched,
        events_count=int(fields["events_count"]) if fields.get("events_count") else None,
        decisions=decisions or None,
        open_questions=open_questions or None,
    )


def parse_created(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def project_matches(memory: Memory, project: str | None) -> bool:
    if not project:
        return True
    return (memory.project or "").casefold() == project.casefold()


def all_memories(root: Path, project: str | None = None) -> list[Memory]:
    ensure_memories_dir(root)
    memories = [memory for path in root.glob("*.md") if (memory := parse_memory(path))]
    scoped = [memory for memory in memories if project_matches(memory, project)]
    return sorted(scoped, key=lambda memory: memory.created or "", reverse=True)


def recent_memories(root: Path, days: int, project: str | None = None) -> list[Memory]:
    cutoff = datetime.now().astimezone() - timedelta(days=days)
    recent: list[Memory] = []
    for memory in all_memories(root, project=project):
        created = parse_created(memory.created)
        if created and created >= cutoff:
            recent.append(memory)
    return recent


def recall_memories(
    root: Path,
    query: str | None = None,
    entity: str | None = None,
    limit: int = 20,
    project: str | None = None,
) -> list[Memory]:
    query_normalized = query.casefold() if query else None
    entity_normalized = entity.casefold() if entity else None
    results: list[Memory] = []

    for memory in all_memories(root, project=project):
        if query_normalized:
            searchable = f"{memory.summary or ''} {memory.body}".casefold()
            if query_normalized not in searchable:
                continue
        if entity_normalized:
            if not any(item.casefold() == entity_normalized for item in memory.entities):
                continue
        results.append(memory)

    if limit > 0:
        return results[:limit]
    return results


def body_preview(body: str, length: int = 200) -> str:
    return body[:length] + "..." if len(body) > length else body


def _jaccard_similarity(a: list[str], b: list[str]) -> float:
    set_a = set(a)
    set_b = set(b)
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def auto_flush_if_needed(
    *,
    root: Path,
    agent: str,
    project: str | None = None,
    flush_count: int = DEFAULT_FLUSH_COUNT,
    flush_minutes: int = DEFAULT_FLUSH_MINUTES,
    jaccard_threshold: float = DEFAULT_JACCARD_THRESHOLD,
) -> Path | None:
    buf = EventBuffer(root=root, project=project, flush_count=flush_count, flush_minutes=flush_minutes)
    if not buf.should_flush():
        return None

    recent = all_memories(root, project=project)
    recent_entities: list[str] = []
    for m in recent[:3]:
        recent_entities.extend(m.entities)

    events = buf.events
    event_entities = [e.entity for e in events if e.entity]
    if recent_entities and event_entities:
        sim = _jaccard_similarity(recent_entities, event_entities)
        if sim > jaccard_threshold:
            return None

    files_touched = list({e.file_path for e in events if e.file_path})
    all_entities = list({e.entity for e in events if e.entity})
    summaries = [e.summary for e in events]
    body = "## Auto-Flush Events\n\n" + "\n".join(f"- [{e.event_type}] {e.summary}" for e in events)

    path = write_segment(
        root=root,
        agent=agent,
        summary=f"Auto-flush: {len(events)} events",
        body=body,
        source="auto-flush",
        files_touched=files_touched,
        entities=all_entities,
        events_count=len(events),
        project=project,
    )
    buf.clear()
    return path


def write_digest(
    *,
    root: Path,
    agent: str,
    summary: str,
    project: str | None = None,
) -> Path | None:
    recent = recent_memories(root, days=1, project=project)
    segments = [m for m in recent if m.type == "segment"]
    if not segments:
        return None

    all_entities: list[str] = []
    seg_refs: list[str] = []
    for seg in segments:
        all_entities.extend(seg.entities)
        seg_refs.append(f"- [{seg.summary}]({seg.filename})")

    body = f"## Session Digest\n\nSegments this session: {len(segments)}\n\n" + "\n".join(seg_refs)
    unique_entities = list(dict.fromkeys(all_entities))

    return write_memory(
        root=root,
        memory_type="session_digest",
        agent=agent,
        entities=unique_entities,
        summary=summary,
        body=body,
        project=project,
    )
