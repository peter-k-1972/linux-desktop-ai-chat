"""
Read-only Snapshots für Control Center und Dashboard.

Keine GUI-Imports. Liefert tabellarische Daten aus echter Infrastruktur
(SQLite-Pfad, RAG-Basis, Ollama-Erreichbarkeit, eingebaute Tools).
"""

from __future__ import annotations

import json
import logging
import sqlite3
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

OLLAMA_TAGS_URL = "http://127.0.0.1:11434/api/tags"
OLLAMA_PROBE_TIMEOUT_SEC = 1.5


@dataclass(frozen=True)
class ToolSnapshotRow:
    tool_id: str
    category: str
    permissions: str
    status: str


@dataclass(frozen=True)
class DataStoreSnapshotRow:
    store: str
    store_type: str
    connection: str
    state: str


def _try_get_infrastructure():
    try:
        from app.services.infrastructure import get_infrastructure

        return get_infrastructure()
    except Exception as exc:
        logger.debug("infrastructure unavailable: %s", exc)
        return None


def _sqlite_probe(db_path: str) -> Tuple[str, str]:
    """
    Kurz-Probe auf die App-DB (read-only).

    Bewusst **kein** Zugriff über Workflow-/Audit-Repositories: nur Erreichbarkeit
    und einfache Integrität für Dashboard/Control-Center-Snapshots.
    """
    p = Path(db_path).expanduser()
    if not p.exists():
        return "Keine Datei", f"Pfad existiert nicht: {p}"
    try:
        conn = sqlite3.connect(f"file:{p}?mode=ro", uri=True, timeout=2.0)
        try:
            conn.execute("SELECT 1")
        finally:
            conn.close()
        return "OK", str(p.resolve())
    except sqlite3.Error as e:
        return "Fehler", str(e)


def fetch_ollama_tag_names(base_url: Optional[str] = None) -> Tuple[Optional[List[str]], str]:
    """
    Lädt Modellnamen von GET /api/tags (synchron, kurzer Timeout).
    Returns: (names, detail) — names ist None bei Fehler oder Parsefehler.
    """
    base = (base_url or "http://127.0.0.1:11434").rstrip("/")
    url = f"{base}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=OLLAMA_PROBE_TIMEOUT_SEC) as resp:
            if resp.status != 200:
                return None, f"HTTP {resp.status}"
            raw = resp.read().decode()
            data = json.loads(raw)
            models = data.get("models") or []
            names: List[str] = []
            for m in models:
                if isinstance(m, dict):
                    n = m.get("name")
                    if n:
                        names.append(str(n))
            return names, base
    except urllib.error.URLError as e:
        return None, str(e.reason) if e.reason else str(e)
    except Exception as e:
        return None, str(e)


def probe_ollama_localhost(base_url: Optional[str] = None) -> Tuple[bool, str]:
    """
    Synchrone Erreichbarkeitsprüfung (kein aiohttp).
    base_url: z.B. http://localhost:11434 — es wird /api/tags angefragt.
    """
    base = (base_url or "http://127.0.0.1:11434").rstrip("/")
    url = f"{base}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=OLLAMA_PROBE_TIMEOUT_SEC) as resp:
            if resp.status == 200:
                return True, base
            return False, f"HTTP {resp.status}"
    except urllib.error.URLError as e:
        return False, str(e.reason) if e.reason else str(e)
    except Exception as e:
        return False, str(e)


def _rag_base_path() -> Path:
    try:
        from app.services.knowledge_service import get_knowledge_service

        return get_knowledge_service().base_path
    except Exception:
        try:
            from app.rag.service import get_default_rag_path

            return Path(get_default_rag_path())
        except Exception:
            return Path("rag_data")


def _chroma_status_for_rag_base(base: Path) -> Tuple[str, str]:
    if not base.exists():
        return "Leer", f"RAG-Basis fehlt: {base}"
    try:
        import chromadb  # noqa: F401
    except ImportError:
        return "Modul fehlt", "chromadb nicht installiert"
    sqlite_files = list(base.rglob("chroma.sqlite3"))[:8]
    if not sqlite_files:
        return "Kein Index", f"Kein chroma.sqlite3 unter {base}"
    return "OK", f"{len(sqlite_files)} Store(s) unter {base}"


def build_data_store_rows() -> List[DataStoreSnapshotRow]:
    rows: List[DataStoreSnapshotRow] = []
    infra = _try_get_infrastructure()
    db_path = "chat_history.db"
    if infra is not None:
        db_path = getattr(infra.database, "db_path", None) or db_path
    st, detail = _sqlite_probe(db_path)
    rows.append(
        DataStoreSnapshotRow(
            store="Chat / App-DB",
            store_type="SQLite",
            connection=detail[:80] + ("…" if len(detail) > 80 else ""),
            state=st,
        )
    )

    rag_base = _rag_base_path()
    cst, cdet = _chroma_status_for_rag_base(rag_base)
    rows.append(
        DataStoreSnapshotRow(
            store="RAG / Vektor-Index",
            store_type="ChromaDB",
            connection=str(rag_base.resolve()) if rag_base.exists() else str(rag_base),
            state=cst,
        )
    )

    rows.append(
        DataStoreSnapshotRow(
            store="RAG-Dateien",
            store_type="Dateisystem",
            connection=str(rag_base.resolve()) if rag_base.exists() else str(rag_base),
            state="OK" if rag_base.exists() else "Fehlt",
        )
    )
    return rows


def build_data_store_health_summary(rows: List[DataStoreSnapshotRow]) -> List[Tuple[str, str, str]]:
    """Label, Kurzstatus, Farbhinweis css-näher (#hex für grün/rot/grau)."""
    out: List[Tuple[str, str, str]] = []
    for r in rows:
        color = "#64748b"
        if r.state == "OK":
            color = "#10b981"
        elif r.state in ("Fehler", "Modul fehlt"):
            color = "#ef4444"
        out.append((r.store, r.state, color))
    return out


def build_tool_snapshot_rows() -> List[ToolSnapshotRow]:
    infra = _try_get_infrastructure()
    settings = infra.settings if infra is not None else None

    rows: List[ToolSnapshotRow] = []

    rows.append(
        ToolSnapshotRow(
            tool_id="filesystem_tools",
            category="Datei",
            permissions="Nur freigegebene Pfade (Chat)",
            status="Verfügbar",
        )
    )

    try:
        from app.tools.web_search import get_ollama_api_key

        key_ok = bool(get_ollama_api_key())
    except Exception:
        key_ok = False
    web_enabled = bool(getattr(settings, "web_search", False)) if settings is not None else False
    if key_ok:
        ws = "API-Key gesetzt"
    elif web_enabled:
        ws = "Key fehlt (OLLAMA_API_KEY / .env)"
    else:
        ws = "In Einstellungen aus; Key optional für Cloud-Suche"
    rows.append(
        ToolSnapshotRow(
            tool_id="web_search",
            category="Suche",
            permissions="Netzwerk (Ollama Cloud)",
            status=ws,
        )
    )

    rag_on = bool(getattr(settings, "rag_enabled", False)) if settings is not None else False
    rows.append(
        ToolSnapshotRow(
            tool_id="rag_augmentation",
            category="RAG",
            permissions="Lesen (Index)",
            status="Aktiv im Chat" if rag_on else "In Einstellungen deaktiviert",
        )
    )

    rows.append(
        ToolSnapshotRow(
            tool_id="slash_commands",
            category="Chat",
            permissions="Parse / Kommandos",
            status="Eingebaut (siehe chat_commands)",
        )
    )
    return rows
