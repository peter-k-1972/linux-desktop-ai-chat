"""
HTML- und Markup-Bereinigung für LLM-Antworten.

Behandelt:
- HTML-Entities dekodieren
- <br> -> Zeilenumbrüche
- Block-Tags -> Absätze
- Inline-Tags glätten
- Markdown und Codeblöcke erhalten
"""

import html
import re
from typing import Tuple


# HTML-Entities werden über html.unescape dekodiert
# Block-Elemente für Absatz-Umwandlung
_BLOCK_TAGS = (
    "div", "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "pre", "ul", "ol", "li", "header", "footer",
    "section", "article", "nav", "hr",
)
# Inline-Tags: Inhalt behalten, Tag entfernen
_INLINE_TAGS = ("b", "i", "u", "strong", "em", "span", "a", "code")
# Zeilenumbrüche
_BR_LIKE = ("br", "br/", "br /")


def _is_code_block(text: str, pos: int) -> bool:
    """Prüft, ob pos innerhalb eines Markdown-Codeblocks liegt."""
    before = text[:pos]
    # Zähle ``` vor pos
    opens = len(re.findall(r"```(?!\s)", before))
    closes = len(re.findall(r"```\s*", before))
    return opens > closes


def _is_inline_code(text: str, pos: int) -> bool:
    """Prüft, ob pos innerhalb von `inline code` liegt."""
    before = text[:pos]
    # Ungerade Anzahl von Backticks vor pos = in Code
    backticks = before.count("`")
    return backticks % 2 == 1


class ResponseCleaner:
    """
    Bereinigt HTML-artige und Markup-Reste in LLM-Antworten.

    Konfigurierbar:
    - strip_html: HTML-Tags entfernen
    - preserve_markdown: Markdown und Codeblöcke möglichst erhalten
    """

    def __init__(
        self,
        strip_html: bool = True,
        preserve_markdown: bool = True,
    ):
        self.strip_html = strip_html
        self.preserve_markdown = preserve_markdown

    def clean(self, text: str) -> Tuple[str, bool]:
        """
        Bereinigt den Text.

        Returns:
            (cleaned_text, had_html)
        """
        if not text or not isinstance(text, str):
            return ("", False)

        raw = text.strip()
        if not raw:
            return ("", False)

        had_html = False

        # 1. HTML-Entities dekodieren
        try:
            decoded = html.unescape(raw)
        except Exception:
            decoded = raw

        # 2. <br> und Varianten in Zeilenumbrüche
        br_pattern = re.compile(
            r"<br\s*/?>",
            re.IGNORECASE,
        )
        if br_pattern.search(decoded):
            had_html = True
        decoded = br_pattern.sub("\n", decoded)

        # 3. Block-Tags: Inhalt behalten, Tag durch Absatz ersetzen
        for tag in _BLOCK_TAGS:
            pattern = re.compile(
                rf"<\s*{tag}\s*[^>]*>(.*?)</\s*{tag}\s*>",
                re.IGNORECASE | re.DOTALL,
            )
            if pattern.search(decoded):
                had_html = True
            decoded = pattern.sub(r"\n\1\n", decoded)

            # Selbstschließende Block-Tags
            self_closing = re.compile(
                rf"<\s*{tag}\s*[^>]*\s*/>",
                re.IGNORECASE,
            )
            decoded = self_closing.sub("\n", decoded)

        # 4. Inline-Tags: nur Inhalt behalten
        for tag in _INLINE_TAGS:
            pattern = re.compile(
                rf"<\s*{tag}\s*[^>]*>(.*?)</\s*{tag}\s*>",
                re.IGNORECASE | re.DOTALL,
            )
            if pattern.search(decoded):
                had_html = True
            decoded = pattern.sub(r"\1", decoded)

        # 4b. <think>...</think> Blöcke entfernen (Thinking-Inhalt im Text)
        think_pattern = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
        if think_pattern.search(decoded):
            had_html = True  # Markup-artig
            decoded = think_pattern.sub("", decoded)

        # 5. Restliche HTML-Tags entfernen (ohne Codeblöcke zu zerstören)
        if self.strip_html:
            # Einfache Tag-Entfernung, außer in Codeblöcken
            def _tag_replacer(match: re.Match) -> str:
                full = match.group(0)
                start = match.start()
                if self.preserve_markdown and _is_code_block(decoded, start):
                    return full
                if self.preserve_markdown and _is_inline_code(decoded, start):
                    return full
                return ""

            # Nur echte HTML-Tags (Buchstabe nach <), nicht < oder > aus Entities
            tag_pattern = re.compile(r"<[a-zA-Z][^>]*>", re.IGNORECASE)
            decoded = tag_pattern.sub(_tag_replacer, decoded)

        # 6. Mehrfache Leerzeilen auf max. 2 reduzieren
        decoded = re.sub(r"\n{3,}", "\n\n", decoded)

        # 7. Leerraum am Anfang/Ende
        decoded = decoded.strip()

        return (decoded, had_html)

    def is_empty_or_junk(self, text: str) -> bool:
        """
        Erkennt leere oder unbrauchbare Antworten:
        - nur Whitespace
        - nur HTML-Reste (nach Bereinigung leer)
        - nur Thinking-Reste (<think>...</think>)
        """
        if not text or not isinstance(text, str):
            return True

        s = text.strip()
        if not s:
            return True

        # Nur HTML-Tags ohne lesbaren Inhalt
        cleaned, _ = self.clean(s)
        if not cleaned or not cleaned.strip():
            return True

        # Nur <think>...</think> Block
        think_pattern = re.compile(r"^\s*<think>.*?</think>\s*$", re.IGNORECASE | re.DOTALL)
        if think_pattern.match(s):
            return True

        return False
