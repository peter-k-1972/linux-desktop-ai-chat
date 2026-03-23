"""
Reine Darstellungslogik für Modellaufruf-Metadaten (kein Qt).

GUI konsumiert strukturierte Dicts für Labels/Tooltips.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.runtime.model_invocation import MODEL_INVOCATION_CHUNK_KEY
from app.services.model_chat_runtime import (
    ERROR_KIND_CONFIG_ERROR,
    ERROR_KIND_POLICY_BLOCK,
    ERROR_KIND_PROVIDER_ERROR,
)


def merge_model_invocation_payload(
    previous: Optional[Dict[str, Any]], chunk: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Letzte Chunk-Werte gewinnen (Stream-Ende überschreibt Teilantworten)."""
    inv = chunk.get(MODEL_INVOCATION_CHUNK_KEY)
    if not isinstance(inv, dict):
        return previous
    base = dict(previous or {})
    base.update(inv)
    return base


def error_kind_from_chunk(chunk: Dict[str, Any]) -> Optional[str]:
    v = chunk.get("error_kind")
    return str(v) if v else None


def build_chat_invocation_view(
    merged_invocation: Optional[Dict[str, Any]],
    *,
    last_error_text: Optional[str],
    last_error_kind: Optional[str],
    completion_status_db: Optional[str],
    model_name: str,
) -> Dict[str, Any]:
    """
    Liefert Schlüssel für die Chat-Detailansicht.

    Keys: title, status_line, detail_lines (list str), style_hint
    style_hint: ok | warn | block | error | cancel | neutral
    """
    inv = merged_invocation or {}
    outcome = (inv.get("outcome") or "").strip().lower()
    preflight = (inv.get("preflight_decision") or "").strip().lower()
    warning_active = bool(inv.get("warning_active"))
    block_reason = (inv.get("block_reason") or inv.get("preflight_message") or "").strip()

    err_kind = last_error_kind or ""
    err_txt = (last_error_text or "").strip()

    # Cancel aus DB-Completion, wenn Runtime kein finales Invocation lieferte
    if not outcome and (completion_status_db or "").lower() in ("interrupted", "possibly_truncated"):
        if "abgebrochen" in (err_txt or "").lower() or not err_txt:
            outcome = "cancelled"

    lines: list[str] = []
    style = "neutral"

    pt = inv.get("prompt_tokens")
    ct = inv.get("completion_tokens")
    tt = inv.get("total_tokens")
    exact = inv.get("token_counts_exact")
    lat = inv.get("latency_ms")

    if pt is not None and ct is not None:
        tot = tt if tt is not None else (int(pt) + int(ct))
        qual = "exakt" if exact is True else ("geschätzt" if exact is False else "—")
        lines.append(f"Prompt: {pt} · Completion: {ct} · Summe: {tot} ({qual})")
    elif tt is not None:
        qual = "exakt" if exact is True else ("geschätzt" if exact is False else "—")
        lines.append(f"Tokens gesamt: {tt} ({qual})")

    if lat is not None:
        lines.append(f"Laufzeit: {lat} ms")

    if err_kind == ERROR_KIND_POLICY_BLOCK or outcome == "policy_block":
        title = "Anfrage blockiert (Limit)"
        status = block_reason or "Quota- oder Richtlinienlimit."
        lines.insert(0, status)
        style = "block"
        return {
            "title": title,
            "status_line": status,
            "detail_lines": lines,
            "style_hint": style,
        }

    if err_kind == ERROR_KIND_CONFIG_ERROR or outcome in ("config_error",):
        title = "Konfiguration"
        status = err_txt or "API-Key oder Anbindung prüfen."
        lines.insert(0, status)
        style = "error"
        return {
            "title": title,
            "status_line": status,
            "detail_lines": lines,
            "style_hint": style,
        }

    if outcome == "cancelled":
        title = "Modellaufruf abgebrochen"
        status = "Generierung manuell oder durch Kontext abgebrochen."
        lines.insert(0, status)
        style = "cancel"
        return {
            "title": title,
            "status_line": status,
            "detail_lines": [x for x in lines if x],
            "style_hint": style,
        }

    if err_kind == ERROR_KIND_PROVIDER_ERROR or outcome in ("provider_error", "failed"):
        title = "Provider- oder Laufzeitfehler"
        status = err_txt or "Der Modellanbieter hat einen Fehler gemeldet."
        if _looks_like_model_missing(err_txt, model_name):
            title = "Modell nicht verfügbar"
            status = err_txt or f"Modell „{model_name}“ ist auf dem Endpoint nicht erreichbar oder nicht installiert."
        lines.insert(0, status)
        style = "error"
        return {
            "title": title,
            "status_line": status,
            "detail_lines": lines,
            "style_hint": style,
        }

    if err_txt and not outcome:
        title = "Fehler"
        lines.insert(0, err_txt)
        style = "error"
        return {
            "title": title,
            "status_line": err_txt,
            "detail_lines": lines,
            "style_hint": style,
        }

    if warning_active or preflight == "allow_with_warning":
        warn_msg = (inv.get("preflight_message") or "").strip() or "Hinweis: Budget- oder Quota-Warnschwelle."
        lines.insert(0, warn_msg)
        style = "warn"
        return {
            "title": "Letzter Modellaufruf",
            "status_line": warn_msg,
            "detail_lines": lines,
            "style_hint": style,
        }

    if outcome == "success" or (pt is not None and not err_txt):
        return {
            "title": "Letzter Modellaufruf",
            "status_line": "Erfolgreich.",
            "detail_lines": lines,
            "style_hint": "ok",
        }

    return {
        "title": "Letzter Modellaufruf",
        "status_line": "Keine Nutzungsdaten für den letzten Lauf.",
        "detail_lines": lines,
        "style_hint": "neutral",
    }


def _looks_like_model_missing(error_text: str, model_name: str) -> bool:
    t = (error_text or "").lower()
    if not t:
        return False
    needles = ("not found", "404", "unknown model", "model ", "does not exist", "nicht gefunden")
    return any(n in t for n in needles) and bool((model_name or "").strip())
