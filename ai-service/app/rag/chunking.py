"""Markdown chunking: front-matter parsing + header-aware splitting with a
recursive size cap. Sizes are in characters (~4 chars/token): 3200 chars ≈ 800
tokens per chunk, 480 chars ≈ 120 tokens of overlap."""

import re
from dataclasses import dataclass, field

MAX_CHUNK_CHARS = 3200
OVERLAP_CHARS = 480

_FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_HEADER_RE = re.compile(r"^(#{1,3})\s+(.*)$", re.MULTILINE)


@dataclass
class ChunkData:
    heading: str
    content: str


@dataclass
class ParsedDocument:
    title: str
    category: str
    body: str
    tags: list[str] = field(default_factory=list)


def parse_front_matter(text: str, fallback_title: str = "") -> ParsedDocument:
    match = _FRONT_MATTER_RE.match(text)
    meta: dict[str, str] = {}
    body = text
    if match:
        body = text[match.end():]
        for line in match.group(1).splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip().lower()] = value.strip().strip("'\"")
    tags_raw = meta.get("tags", "")
    tags = [t.strip() for t in tags_raw.strip("[]").split(",") if t.strip()]
    return ParsedDocument(
        title=meta.get("title", fallback_title),
        category=meta.get("category", "IT").upper(),
        body=body.strip(),
        tags=tags,
    )


def _split_by_size(text: str) -> list[str]:
    """Recursive fallback for sections longer than MAX_CHUNK_CHARS: split on
    paragraph boundaries, keeping OVERLAP_CHARS of trailing context."""
    if len(text) <= MAX_CHUNK_CHARS:
        return [text]
    paragraphs = text.split("\n\n")
    parts: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) > MAX_CHUNK_CHARS and current:
            parts.append(current)
            current = current[-OVERLAP_CHARS:] + "\n\n" + paragraph
        else:
            current = candidate
    if current.strip():
        parts.append(current)
    # A single paragraph can still exceed the cap; hard-split it.
    result: list[str] = []
    for part in parts:
        while len(part) > MAX_CHUNK_CHARS:
            result.append(part[:MAX_CHUNK_CHARS])
            part = part[MAX_CHUNK_CHARS - OVERLAP_CHARS:]
        result.append(part)
    return [p.strip() for p in result if p.strip()]


def chunk_markdown(body: str) -> list[ChunkData]:
    """Split on #/##/### headers, then enforce the size cap per section."""
    matches = list(_HEADER_RE.finditer(body))
    sections: list[tuple[str, str]] = []
    if not matches:
        sections.append(("", body))
    else:
        preamble = body[: matches[0].start()].strip()
        if preamble:
            sections.append(("", preamble))
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            heading = match.group(2).strip()
            section_text = body[match.start():end].strip()
            if section_text:
                sections.append((heading, section_text))

    chunks: list[ChunkData] = []
    for heading, section_text in sections:
        for piece in _split_by_size(section_text):
            chunks.append(ChunkData(heading=heading[:255], content=piece))
    return chunks
