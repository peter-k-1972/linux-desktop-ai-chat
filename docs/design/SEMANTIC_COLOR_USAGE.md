# Semantic Color Usage

**Zweck:** Einheitliche Verwendung von **Success**, **Warning**, **Error**, **Info** für Zustände und Feedback — getrennt von **Accent** (Marke/Fokus).  
**Token-Basis:** `color.state.success|warning|error|info`, `color.badge.*`, `color.console.*`, `color.indicator.*`, `color.graph.node.status.*`, `color.fg.on_*` wo zutreffend.

---

## 1. Success

| Verwendung | Beispiele in der App | Tokens |
|------------|----------------------|--------|
| **Erfolgreiche Aktion / abgeschlossener Schritt** | Workflow-Knoten „completed“, Deployment „released“, gespeichert | `STATE_SUCCESS`, `GRAPH_NODE_STATUS_COMPLETED_*` |
| **Positive Status-Badges** | „Healthy“, „OK“, „Running (good)“ wenn semantisch Erfolg | `BADGE_SUCCESS_*` |
| **Log-/Konsolenzeilen (positiv)** | „Build succeeded“, Verbindung hergestellt | `CONSOLE_SUCCESS` |
| **Indikatoren „bereit“** | Dienst verfügbar | `INDICATOR_READY` (kann mit Success-Palette harmonieren) |

**Nicht:** Normale Nav- oder Tab-Aktivzustände (das ist Accent, nicht Success).

---

## 2. Warning

| Verwendung | Beispiele | Tokens |
|------------|-----------|--------|
| **Aufmerksamkeit ohne Abbruch** | Quota fast erreicht, deprecated API, Retry empfohlen | `STATE_WARNING`, `BADGE_WARNING_*` |
| **Validierung (weich)** | Feld ausfüllbar, aber Hinweis | Warning-Badge oder Rand — nicht Error |
| **Logs** | Deprecation, Rate-Limit | `CONSOLE_WARNING` |
| **Workflow** | „cancelled“ oder wartender Zustand je nach Produktdefinition | ggf. `GRAPH_NODE_STATUS_CANCELLED_*` oder eigene neutrale Tönung — **konsistent dokumentieren** |

---

## 3. Error

| Verwendung | Beispiele | Tokens |
|------------|-----------|--------|
| **Fehlgeschlagene Aktion** | Request failed, Save failed | `STATE_ERROR`, `BADGE_ERROR_*` |
| **Validierung (hart)** | Pflichtfeld leer, ungültiges Format | Error-Text + optional Border |
| **Logs / Konsole** | Stacktrace-Kurzinfo, ERROR-Level | `CONSOLE_ERROR` |
| **Workflow-Knoten** | `failed` | `GRAPH_NODE_STATUS_FAILED_*` |
| **Indikatoren** | `INDICATOR_FAILED` |

**Kontrast:** Vordergrund auf farbigem Badge über `FG_ON_ERROR` o. ä. sicherstellen (Spec).

---

## 4. Info

| Verwendung | Beispiele | Tokens |
|------------|-----------|--------|
| **Neutrale Mitteilungen** | „Wird geladen…“, Hinweisboxen ohne Warncharakter | `STATE_INFO`, `BADGE_INFO_*` |
| **System-/Meta-Chat** | Systemnachrichten in Chat (optional leicht info-tinted) | `CHAT_SYSTEM_*` kann info-nah sein |
| **Konsolen INFO-Zeilen** | `CONSOLE_INFO` |
| **Tooltips / Inline-Hilfe** | In der Regel **kein** Info-Blau als Hintergrund; eher neutrale Tooltip-Tokens (`TOOLTIP_*`) |

**Abgrenzung:** Info ist **nicht** Ersatz für Links (Links = Accent-Kanal `FG_LINK` / `MARKDOWN_LINK`).

---

## 5. Kombinationsregeln

1. **Pro UI-Element höchstens eine dominante Semantic-Rolle** (nicht gleichzeitig Error-Badge und Warning-Rahmen ohne Hierarchie).  
2. **Semantic schlägt Accent** auf demselben Control (z. B. fehlerhaftes Eingabefeld: Error-Border vor Accent-Focus — oder Focus-Ring zusätzlich barrierefrei).  
3. **Dashboard-KPIs:** Nur bei echtem Status semantic einfärben; sonst neutrale Zahlen + ggf. dezente Sparkline (Chart-Tokens).  
4. **Markdown:** Semantic nur in vom Renderer explizit markierten Blöcken (z. B. Admonitions, falls eingeführt); Standard-Body bleibt neutral.

---

## 6. Checkliste für neue Features

- [ ] Braucht die Meldung eine **Handlung** (Accent/Link) oder einen **Zustand** (Semantic)?  
- [ ] Ist die Farbe **barrierefreier Kontrast** zum Hintergrund (siehe `THEME_CONTRAST_RULES.md`)?  
- [ ] Wiederholen wir dieselbe Semantik wie an anderer Stelle (Badges = Badges, Logs = Console)?  

---

*Ende Semantic Map.*
