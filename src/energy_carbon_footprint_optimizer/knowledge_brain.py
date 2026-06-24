from pathlib import Path
from typing import List
import re
from .constants import FRAMEWORKS
from .models import EvidenceSource


def load_brain_sources(path: str = None) -> List[EvidenceSource]:
    '''Load fallback evidence sources from SECOND-KNOWLEDGE-BRAIN.md and the framework catalog.'''
    if path:
        brain_path = Path(path)
    else:
        brain_path = Path(__file__).resolve().parent.parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"

    sources: List[EvidenceSource] = []

    if brain_path.exists():
        text = brain_path.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            parts = [p.strip() for p in stripped.split("|")]
            parts = [p for p in parts if p and not p.startswith("--")]
            if len(parts) < 5:
                continue
            if "Title" in parts[0] or parts[0] in ("Framework / Method", "Title"):
                continue
            title, authors, year, venue, url, *rest = parts
            finding = rest[0] if rest else ""
            try:
                y = int(year) if year.isdigit() else None
            except ValueError:
                y = None
            sources.append(
                EvidenceSource(
                    title=title,
                    url=url,
                    year=y,
                    tier="SECOND-KNOWLEDGE-BRAIN fallback",
                    finding=finding,
                )
            )

    # Always include the canonical framework sources as a guaranteed baseline.
    for fw in FRAMEWORKS:
        sources.append(
            EvidenceSource(
                title=fw["name"],
                url=fw["url"],
                tier="Framework / Standard document",
                finding="Core methodology",
            )
        )

    # Deduplicate by URL (falling back to title).
    seen = set()
    deduped: List[EvidenceSource] = []
    for s in sources:
        key = s.url or s.title
        if key and key not in seen:
            seen.add(key)
            deduped.append(s)
    return deduped
