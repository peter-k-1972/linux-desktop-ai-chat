"""
Document Loader – lädt Dokumente aus verschiedenen Quellen.

Unterstützte Formate: Markdown, Text, Python, JSON.
PDF optional vorbereitet.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import List, Optional

from app.rag.models import Document

logger = logging.getLogger(__name__)

# Unterstützte Dateiendungen
SUPPORTED_EXTENSIONS = {".md", ".txt", ".py", ".json"}
OPTIONAL_EXTENSIONS = {".pdf"}  # Vorbereitet, nicht zwingend implementiert


class DocumentLoadError(Exception):
    """Fehler beim Laden eines Dokuments."""

    pass


def _compute_doc_id(path: str, content: str) -> str:
    """Erzeugt eine stabile Dokument-ID aus Pfad und Inhalt."""
    raw = f"{path}:{len(content)}:{content[:500]}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _load_text_file(path: Path, encoding: str = "utf-8") -> str:
    """Lädt eine Textdatei mit Fallback-Encoding."""
    try:
        return path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception as e:
            raise DocumentLoadError(f"Encoding-Fehler bei {path}: {e}") from e
    except Exception as e:
        raise DocumentLoadError(f"Lesefehler bei {path}: {e}") from e


def _load_json_file(path: Path) -> str:
    """Lädt JSON und gibt als formatierte Zeichenkette zurück."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(data, ensure_ascii=False, indent=2)
    except json.JSONDecodeError as e:
        raise DocumentLoadError(f"Ungültiges JSON in {path}: {e}") from e
    except Exception as e:
        raise DocumentLoadError(f"Lesefehler bei {path}: {e}") from e


def _load_pdf_file(path: Path) -> str:
    """
    Lädt PDF-Inhalt (optional).
    Erfordert pypdf oder pdfplumber. Gibt leeren String, wenn nicht verfügbar.
    """
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
        return "\n\n".join(parts) if parts else ""
    except ImportError:
        logger.warning("pypdf nicht installiert – PDF-Support deaktiviert")
        return ""
    except Exception as e:
        logger.warning("PDF-Lesefehler %s: %s", path, e)
        return ""


def load_document(path: str) -> Document:
    """
    Lädt ein einzelnes Dokument und erzeugt ein Document-Objekt.

    Args:
        path: Dateipfad zum Dokument

    Returns:
        Document mit content und metadata

    Raises:
        DocumentLoadError: Bei Lesefehlern oder nicht unterstütztem Format
    """
    p = Path(path).resolve()
    if not p.exists():
        raise DocumentLoadError(f"Datei existiert nicht: {path}")

    suffix = p.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS and suffix not in OPTIONAL_EXTENSIONS:
        raise DocumentLoadError(
            f"Nicht unterstütztes Format: {suffix}. "
            f"Erlaubt: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    if suffix == ".json":
        content = _load_json_file(p)
    elif suffix == ".pdf":
        content = _load_pdf_file(p)
        if not content:
            raise DocumentLoadError(f"PDF konnte nicht gelesen werden: {path}")
    else:
        content = _load_text_file(p)

    if not content.strip():
        raise DocumentLoadError(f"Leeres Dokument: {path}")

    doc_id = _compute_doc_id(str(p), content)
    metadata = {
        "filename": p.name,
        "extension": suffix,
        "source_type": "file",
    }

    return Document(
        id=doc_id,
        path=str(p),
        content=content,
        metadata=metadata,
        source_type="file",
    )


def load_documents_from_directory(
    directory: str,
    *,
    extensions: Optional[set] = None,
    recursive: bool = True,
) -> List[Document]:
    """
    Lädt alle unterstützten Dokumente aus einem Verzeichnis.

    Args:
        directory: Pfad zum Verzeichnis
        extensions: Optionale Menge von Endungen (Default: SUPPORTED_EXTENSIONS)
        recursive: Auch Unterverzeichnisse durchsuchen

    Returns:
        Liste von Document-Objekten (Fehler werden geloggt, nicht geworfen)
    """
    ext = extensions or SUPPORTED_EXTENSIONS
    root = Path(directory).resolve()
    if not root.is_dir():
        logger.warning("Verzeichnis existiert nicht: %s", directory)
        return []

    pattern = "**/*" if recursive else "*"
    docs: List[Document] = []

    for f in root.glob(pattern):
        if not f.is_file():
            continue
        if f.suffix.lower() not in ext:
            continue
        try:
            docs.append(load_document(str(f)))
        except DocumentLoadError as e:
            logger.warning("Dokument übersprungen %s: %s", f, e)

    return docs
