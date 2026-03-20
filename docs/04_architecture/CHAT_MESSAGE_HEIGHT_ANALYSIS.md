# Chat-Message Höhenanalyse – Feste/Pseudofeste Höhen

**Stand:** 2026-03-17  
**Problem:** User-Box zu groß, Assistant-Box zu klein; beide nicht aus Inhalt dimensioniert.

---

## 1. Gefundene Höhenlogik

### ChatMessageBubbleWidget (ChatConversationPanel – neue UI)

| Stelle | Code | Problem |
|--------|------|---------|
| _MessageContentEdit.sizeHint | `w = max(1, self.viewport().width())` | **viewport() oft 0 oder falsch** während Layout |
| | `doc.setTextWidth(w)` | Bei w=1: Text 1px breit → riesige Höhe → User zu groß |
| | | Bei w=1200 (Stretch): wenige Zeilen → kleine Höhe → Assistant zu klein |
| | `h = int(doc.size().height()) + 8` | +8 pauschal; max(24,h) |
| setMinimumHeight(0) | Content-Widget | OK, erlaubt Schrumpfen |
| ScrollBarAsNeeded | Vertikal | Kann bei falschem sizeHint zu innerer Scrollbar führen |

### ChatMessageWidget (Legacy ConversationView)

| Stelle | Code | Problem |
|--------|------|---------|
| bubble SizePolicy | `Preferred, MinimumExpanding` | **MinimumExpanding** = nimmt verfügbaren Platz → kurze Nachricht wird riesig |
| QLabel | setWordWrap(True) | Kein sizeHint aus Inhalt; Höhe kommt von Layout |

---

## 2. Ursache

**ChatMessageBubbleWidget:** `viewport().width()` ist während Layout unzuverlässig:
- Vor erstem Layout: 0 → w=1 → doc extrem schmal → Höhe explodiert
- Nach Stretch: viewport kann groß sein → doc wenige Zeilen → Höhe zu klein

**ChatMessageWidget:** `MinimumExpanding` verlangt Expansion → Layout füllt mit verfügbarem Platz.

---

## 3. Fix

1. **_MessageContentEdit.sizeHint:** Stabile Breite für die Berechnung:
   - viewport < 100: Fallback 400
   - viewport > 700: Obergrenze 700 (verhindert zu wenige Zeilen)
   - Keine role-spezifische Logik

2. **ChatMessageWidget:** `MinimumExpanding` → `Minimum` (vertikal)
