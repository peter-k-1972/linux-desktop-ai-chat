# GUI Modernisierung, Tiefe, „Wow“ ohne Kitsch (Phase 4)

**Rahmen:** Struktur (Tokens, Icons, Layout-Governance) gilt als gegeben. Bewertung: räumliche Hierarchie, Materialität, Interaktions-Feedback, Premium-Feeling, Signatur.

---

## 1. Layering / Tiefe

| Bereich | Aktueller Eindruck | Problemzonen | Potenziale | Konkrete Maßnahmen | Priorität | Aufwand/Nutzen |
|---------|-------------------|--------------|------------|------------------|-----------|----------------|
| Workspaces / Cards | Workbench-Patterns (`section_card`, CC-Panel-Frames) | Teilweise noch „flache“ Weiß-Flächen mit hartem Rand (`tools_panels.py` setzt explizites `#fafafa` / Border) | Konsistente **Surface-Stufen** aus Semantic Tokens statt lokaler Hex-Werte | CC-Panels auf `design_tokens` / Theme-Manager umstellen; eine **Raumfarbe** für „eingesenkte“ Tabellen | **Hoch** | Mittel / Hoch |
| Inspector | Kontextabhängig, funktional | Wechsel kann abrupt wirken | **Sanfte Übergänge** (Opacity/Height) nur wo Performance ok | QPropertyAnimation oder gestapeltes Cross-Fade optional | **Mittel** | Mittel / Mittel |
| Dialoge / Docks | Qt-Standard + Governance | Docks können „schwer“ wirken | Klare **Vordergrund**-Hierarchie für modale vs. Dock-Inhalte | Dock-Titelzeilen und Inspector-Header visuell an einen **Header-Profile** angleichen | **Mittel** | Niedrig / Mittel |

---

## 2. Materialität („gebaut“)

| Bereich | Aktueller Eindruck | Potenziale | Maßnahmen | P | A/N |
|---------|-------------------|------------|-----------|---|-----|
| Control Center | Lesbare Karten, erklärende Info-Labels | Wirkt bereits „Produkt-UI“ | Weniger lokales Styling, mehr **kanonische** Panel-Shell | Mittel | Mittel/Mittel |
| Dashboard | Transparente ScrollArea, klare Typo-Hierarchie (`primaryTitle`) | Noch weniger „Dashboard-App-Generic“ | Eine **signaturstarke** erste Karte (z. B. Projekt + System) statt vier gleichgewichteter Kacheln | Hoch | Mittel/Hoch |

---

## 3. Motion / Interaction Polish

| Hebel | Wo | Maßnahme | P | A/N |
|-------|-----|----------|---|-----|
| Hover / Focus | Sidebar, Runtime-Nav-Listen | Deutlichere Focus-Rings (Accessibility) + subtile Hover (bereits Icon-System) | Mittel | Niedrig/Mittel |
| Workspace-Wechsel | `QStackedWidget` | Kurzer Fade optional; vermeiden bei schweren Widgets | Niedrig | Hoch/Niedrig |
| Refresh-Aktionen | CC-Panels „Aktualisieren“ | Kleines „last updated“ + Spinner | Mittel | Niedrig/Mittel |

---

## 4. High-end feel — 20 % für 80 % Wirkung

1. **Ein** konsistentes Oberflächenmodell (keine verstreuten `#e2e8f0` in Feature-Panels) — größter visueller Gewinn bei moderatem Aufwand.  
2. **Dashboard:** erste Zeile als „hero“-artige Zusammenfassung (Projekt + Ollama + QA-Health) statt vier gleichwertiger Karten.  
3. **Inspector:** einheitlicher Empty-State mit Illustration/Icon + nächster Schritt.  
4. **TopBar:** visuelle Gruppierung (Kontext | Navigation | Hilfe) mit Spacing-Token.  
5. **Semantische Ruhe:** Platzhalter-Texte entfernen oder durch ehrliche Empty States ersetzen — wirkt sofort „fertiger“ als jede Animation.

---

## 5. Signature Experience („Obsidian Core / Linux Desktop Chat“)

| Idee | Umsetzung | Risiko |
|------|-----------|--------|
| **„Command Surface“** | Eine wiedererkennbare Kompositionsform: Breadcrumb + kontextueller Inspector + Bottom-Panel — bereits angelegt; verstärken durch konsistente Kantenradien und Akzent **nur** für Primäraktion | Überladung vermeiden |
| **Transparenz-Metapher** | Introspection-Workspace als **Marken-Feature** (Diagnostik sichtbar) — im Help/onboarding hervorheben | Zu technisch für Endnutzer ohne Filter |
| **Deutsch-präzise, ruhige Typo** | Bereits vorhanden; mit englischen Rest-Strings bereinigen | Gering |

---

*Ende GUI_MODERNIZATION_REVIEW.md*
