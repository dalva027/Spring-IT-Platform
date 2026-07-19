from app.rag.chunking import MAX_CHUNK_CHARS, chunk_markdown, parse_front_matter

DOC = """---
title: VPN Access Guide
category: NETWORKING
tags: [vpn, remote-access]
---

Intro paragraph before any header.

## Setup

Install the client.

### Troubleshooting

Restart the tunnel.
"""


def test_parse_front_matter():
    parsed = parse_front_matter(DOC, fallback_title="fallback")
    assert parsed.title == "VPN Access Guide"
    assert parsed.category == "NETWORKING"
    assert "vpn" in parsed.tags
    assert parsed.body.startswith("Intro paragraph")


def test_parse_front_matter_fallbacks():
    parsed = parse_front_matter("just text, no front matter", fallback_title="doc-name")
    assert parsed.title == "doc-name"
    assert parsed.category == "IT"


def test_chunk_markdown_splits_on_headers():
    parsed = parse_front_matter(DOC)
    chunks = chunk_markdown(parsed.body)
    headings = [c.heading for c in chunks]
    assert headings == ["", "Setup", "Troubleshooting"]
    assert "Install the client." in chunks[1].content


def test_chunk_markdown_enforces_size_cap():
    huge_section = "## Big\n\n" + "\n\n".join(f"Paragraph {i} " + "x" * 400 for i in range(40))
    chunks = chunk_markdown(huge_section)
    assert len(chunks) > 1
    assert all(len(c.content) <= MAX_CHUNK_CHARS for c in chunks)
    assert all(c.heading == "Big" for c in chunks)
