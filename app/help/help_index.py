"""
HelpIndex – Kategorien, Navigation, Volltextsuche, Tagging.

Lädt Markdown-Dokumente aus help/ (mit YAML-Frontmatter) und generierte Inhalte.
Fallback: docs/ für Rückwärtskompatibilität.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Kategorien für In-App-Hilfe
HELP_CATEGORIES = [
    ("getting_started", "Erste Schritte"),
    ("operations", "Operations"),
    ("control_center", "Control Center"),
    ("qa_governance", "QA & Governance"),
    ("runtime_debug", "Runtime / Debug"),
    ("settings", "Einstellungen"),
    ("troubleshooting", "Fehlerbehebung"),
    ("architecture", "Architektur"),
    ("models", "Modelle und Provider"),
    ("agents", "Agenten-System"),
    ("rag", "RAG-Wissenssystem"),
    ("prompts", "Prompt-System"),
    ("tools", "Tools und Integrationen"),
    ("ai_studio", "AI Studio"),
    ("media", "Medien-Generierung"),
    ("workflows", "Workflows"),
]

# Mapping: doc-Dateiname -> Kategorie-ID (Fallback für docs/)
DOC_TO_CATEGORY: Dict[str, str] = {
    "introduction": "getting_started",
    "architecture": "architecture",
    "models": "models",
    "agents": "agents",
    "rag": "rag",
    "RAG_ARCHITEKTUR": "rag",
    "prompts": "prompts",
    "tools": "tools",
    "ai_studio": "ai_studio",
    "media_generation": "media",
    "workflows": "workflows",
    "settings": "settings",
    "troubleshooting": "troubleshooting",
}


@dataclass
class HelpTopic:
    """Ein Hilfethema mit Metadaten."""

    id: str
    title: str
    category: str
    content: str
    tags: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)
    workspace: Optional[str] = None
    order: int = 999
    source: str = "help"  # help | docs | generated

    @property
    def category_display(self) -> str:
        for cid, cname in HELP_CATEGORIES:
            if cid == self.category:
                return cname
        return self.category

    def matches_search(self, query: str) -> bool:
        """Volltextsuche: Titel, Inhalt, Tags."""
        q = query.lower().strip()
        if not q:
            return True
        if q in self.title.lower():
            return True
        if q in self.content.lower():
            return True
        for tag in self.tags:
            if q in tag.lower():
                return True
        # Stichwörter
        words = q.split()
        text = f"{self.title} {self.content} {' '.join(self.tags)}".lower()
        return all(w in text for w in words if len(w) >= 2)


def _parse_frontmatter(text: str) -> tuple[Dict[str, Any], str]:
    """Parse YAML frontmatter. Returns (metadata, body)."""
    metadata: Dict[str, Any] = {}
    body = text
    if text.strip().startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                import yaml
                metadata = yaml.safe_load(parts[1]) or {}
            except Exception:
                pass
            body = parts[2].lstrip("\n")
    return metadata, body


class HelpIndex:
    """Index aller Hilfethemen mit Suche und Kategorien."""

    def __init__(self, help_dir: Optional[str] = None, docs_dir: Optional[str] = None):
        self.help_dir = Path(help_dir or self._default_help_dir())
        self.docs_dir = Path(docs_dir or self._default_docs_dir())
        self._topics: Dict[str, HelpTopic] = {}
        self._load_all()

    def _default_help_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent / "help"

    def _default_docs_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent / "docs"

    def _load_all(self):
        """Lädt alle Themen: help/ (priorität), docs/ (Fallback), generiert."""
        self._topics.clear()
        self._load_help()
        self._load_docs()
        self._load_generated()

    def _load_help(self):
        """Lädt Markdown aus help/ mit YAML-Frontmatter."""
        if not self.help_dir.exists():
            return
        for path in self.help_dir.rglob("*.md"):
            try:
                raw = path.read_text(encoding="utf-8")
            except Exception:
                continue
            meta, body = _parse_frontmatter(raw)
            topic_id = meta.get("id") or path.stem
            title = meta.get("title") or self._extract_title(body) or path.stem.replace("_", " ").title()
            category = meta.get("category", "getting_started")
            tags = meta.get("tags") or self._extract_tags(body, topic_id)
            related = meta.get("related") or []
            workspace = meta.get("workspace")
            order = meta.get("order", 999)
            # help/ overrides docs/ and generated
            self._topics[topic_id] = HelpTopic(
                id=topic_id,
                title=title,
                category=category,
                content=body,
                tags=tags if isinstance(tags, list) else [tags],
                related=related if isinstance(related, list) else [],
                workspace=workspace,
                order=order if isinstance(order, int) else 999,
                source="help",
            )

    def _load_docs(self):
        """Lädt Markdown aus docs/ (Fallback, nur wenn help/ keinen Eintrag hat).
        Scannt docs/ und docs/*/ (nummerierte Sektionen), nicht Root-Anker."""
        if not self.docs_dir.exists():
            return
        # Root-Anker überspringen (README, 00_map, SYSTEM_MAP, TRACE_MAP)
        skip_stems = {"README", "00_map_of_the_system", "SYSTEM_MAP", "TRACE_MAP"}
        paths = list(self.docs_dir.glob("*.md")) + list(self.docs_dir.glob("*/*.md"))
        for path in paths:
            if path.stem in skip_stems:
                continue
            doc_id = path.stem
            if doc_id in self._topics:
                continue  # help/ hat Vorrang
            cat = DOC_TO_CATEGORY.get(doc_id, "getting_started")
            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                content = ""
            title = self._extract_title(content) or doc_id.replace("_", " ").title()
            tags = self._extract_tags(content, doc_id)
            self._topics[doc_id] = HelpTopic(
                id=doc_id,
                title=title,
                category=cat,
                content=content,
                tags=tags,
                source="docs",
            )

    def _extract_title(self, content: str) -> Optional[str]:
        """Erster #-Header als Titel."""
        for line in content.splitlines():
            m = re.match(r"^#\s+(.+)$", line.strip())
            if m:
                return m.group(1).strip()
        return None

    def _extract_tags(self, content: str, doc_id: str) -> List[str]:
        """Tags aus Inhalt und doc_id ableiten."""
        tags = [doc_id]
        # Kategorie als Tag
        cat = DOC_TO_CATEGORY.get(doc_id)
        if cat:
            tags.append(cat)
        # Häufige Begriffe als Stichwörter
        words = re.findall(r"\b[A-Za-z]{4,}\b", content.lower())
        from collections import Counter
        common = [w for w, _ in Counter(words).most_common(20) if w not in ("the", "and", "for", "with", "this", "that")]
        tags.extend(common[:5])
        return list(dict.fromkeys(tags))

    def _load_generated(self):
        """Lädt auto-generierte Themen (Agenten, Modelle, Tools, Settings)."""
        from app.help.doc_generator import generate_help_topics
        for topic in generate_help_topics():
            self._topics[topic.id] = topic

    def get_topic(self, topic_id: str) -> Optional[HelpTopic]:
        return self._topics.get(topic_id)

    def get_topic_by_workspace(self, workspace_id: str) -> Optional[HelpTopic]:
        """Liefert das Help-Thema für einen Workspace (Kontexthilfe)."""
        for t in self._topics.values():
            if t.workspace == workspace_id:
                return t
        return None

    def list_by_category(self, category: Optional[str] = None) -> List[HelpTopic]:
        """Themen nach Kategorie, sortiert nach order, dann Titel."""
        items = list(self._topics.values())
        if category:
            items = [t for t in items if t.category == category]
        return sorted(items, key=lambda t: (t.category, t.order, t.title))

    def search(self, query: str) -> List[HelpTopic]:
        """Volltextsuche über alle Themen."""
        if not query.strip():
            return self.list_by_category()
        return [t for t in self._topics.values() if t.matches_search(query)]

    def categories(self) -> List[tuple]:
        """(id, display_name) für alle Kategorien."""
        return list(HELP_CATEGORIES)
