# Chat-Kontext-Semantik – Abschlussreport

**Stand:** 2026-03-17  
**Ziel:** Kontext semantisch wirksam machen – nicht nur formal, sondern für bessere Antworten.

---

## 1. Analysierte Kontextwirkung

### 1.1 Bisher (deklarativ)

- Format: „Kontext: - Projekt: X - Chat: Y - Topic: Z“
- Modell-Reaktion: Kontext oft ignoriert – reine Namensliste ohne Bedeutung
- Keine Steuerung von Antwortstil, Relevanz, Fokussierung

### 1.2 Ursache

- Nur „was“, kein „wie relevant“
- Keine Handlungsanweisung
- Kein Rahmen (Arbeitskontext)

**Dokument:** `docs/04_architecture/CHAT_CONTEXT_SEMANTICS_ANALYSIS.md`

---

## 2. Umgesetzte semantische Erweiterung

### 2.1 Neues Format

```
Arbeitskontext:
- Projekt: XYZ (Themenbereich)
- Chat: Debug Session (laufende Konversation)
- Topic: API (fokussierter Bereich)

Berücksichtige diesen Kontext bei der Antwort.
```

### 2.2 Änderungen

| Element | Vorher | Nachher |
|---------|--------|---------|
| Rahmen | Kontext | Arbeitskontext |
| Projekt | XYZ | XYZ (Themenbereich) |
| Chat | Debug Session | Debug Session (laufende Konversation) |
| Topic | API | API (fokussierter Bereich) |
| Anweisung | — | Berücksichtige diesen Kontext bei der Antwort. |

### 2.3 Längenvergleich

- Vorher: ~55 Zeichen (Beispiel)
- Nachher: ~120 Zeichen (Beispiel)
- Keine Prompt-Explosion – moderater Zuwachs

---

## 3. Verhalten

- **Antwortstil:** Subtil – Kontext berücksichtigen, nicht vorschreiben
- **Relevanz:** Hints erklären „wie relevant“ (Themenbereich, fokussierter Bereich)
- **Fokussierung:** Topic als „fokussierter Bereich“ markiert
- **Kontinuität:** „laufende Konversation“ signalisiert Gesprächsstrang

---

## 4. Tests

| Test | Verifiziert |
|------|-------------|
| test_chat_context_full | Semantische Hints, Anweisung |
| test_semantic_context_not_overloaded | Keine Prompt-Explosion (<250 Zeichen) |
| test_missing_topic_does_not_break | Fehlendes Topic unverändert robust |
| Bestehende Tests | Keine Regression |

---

## 5. Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| app/chat/context.py | to_system_prompt_fragment() semantisch erweitert |
| tests/structure/test_chat_context_injection.py | Assertions für semantisches Format, test_semantic_context_not_overloaded |
| docs/04_architecture/CHAT_CONTEXT_SEMANTICS_ANALYSIS.md | Neu |
| docs/04_architecture/CHAT_CONTEXT_SEMANTICS_REPORT.md | Neu |

---

## 6. Bekannte Grenzen

- **Modell-Varianten:** Unterschiedliche Modelle reagieren unterschiedlich – keine Garantie
- **Keine A/B-Tests:** Manuelle Prüfung empfohlen (neutral vs. semantisch)
- **Generische Hints:** (Themenbereich), (laufende Konversation) sind fest – keine DB-Metadaten

---

## 7. Empfohlene nächste Schritte

1. **Manuelle Variantentests:** Neutral vs. semantisch mit verschiedenen Modellen
2. **Optional:** Konfigurierbarer Semantik-Modus (Settings)
3. **Optional:** Projekt-/Topic-Beschreibung als erweiterter Kontext (wenn in DB)

---

## 8. Ergebnis

Der Chat nutzt Kontext nicht nur formal, sondern **semantisch wirksam**:

- Rahmen „Arbeitskontext“ statt neutralem „Kontext“
- Kurze Hints erklären Bedeutung (Themenbereich, fokussierter Bereich)
- Eine Zeile Anweisung steuert Verhalten subtil
- Keine Prompt-Explosion, keine langen Instruktionen
