# Bewusst zurückgestellte Maßnahmen — Linux Desktop Chat

**Datum:** 2026-03-22  
**Basis:** Audit 2026-03-22 und Backlog IMP-001–012.  
**Zweck:** Explizit festhalten, was **nicht** zuerst angegangen werden soll — mit **Begründung**.

---

## 1. Breite visuelle / kosmetische UX-Politur (ohne Struktur)

**Was:** Pixel, Abstände, Themes, „Feinschliff einzelner Oberflächen“ generisch.  
**Warum zurück:** `RELEASE_ACCEPTANCE_REPORT.md` nennt UX-Polish ohnehin als nicht blockierend; Audit fordert **vorher** Test-/Doku-Wahrheit und Dual-UI-Klarheit (**IMP-001, IMP-002, IMP-004**).  
**Wann sinnvoll:** Nach **Wave 2** (Roadmap), wenn klar ist, **welche** Oberfläche optimiert wird.

---

## 2. Vollständige Workbench-Inspector-Implementierung (IMP-007 groß)

**Was:** Alle Stub-Karten durch echte Daten/Steuerung ersetzen.  
**Warum zurück:** Hoher Aufwand; Workbench ist **nicht** Standardstart — ohne **IMP-004** droht Investition in wahrgenommenes „Nebenprodukt“.  
**Wann sinnvoll:** Nach Rollenklärung; **kleiner** erster Schritt (Copy „Demo“) ist **nicht** zurückgestellt — nur die **große** Implementierung.

---

## 3. Packaging / Installer (IMP-008)

**Was:** PyInstaller, Flathub, o. ä.  
**Warum zurück:** Release-Audit nennt fehlende e2e-Verifizierung; **kein** Nutzen, Installer zu bauen, solange **Haupt-UI-Regression** (IMP-001) und **Doku-Wahrheit** (IMP-002) offen sind — sonst werden **falsche Builds** verteilt.  
**Wann sinnvoll:** Nach Wave 1–2 und definiertem Verteilungsziel.

---

## 4. CLI Replay/Repro in die GUI einbetten (IMP-011)

**Was:** Dialog/Deep-Link für `app/cli/`-Funktionen.  
**Warum zurück:** Großer UI-/Produkt-Entwurf; laut Audit Lücke „ohne Kommandozeile“, aber **erst** sinnvoll, wenn **Chat-Hauptpfad** teststabil ist (**IMP-001**), sonst neue Einstiegspunkte auf brüchiger Basis.  
**Wann sinnvoll:** Nach abgeschlossenem Mindest-IMP-001 und Klarheit in IMP-004/005.

---

## 5. Architektur-Zusammenführung Shell + Workbench zu „einem“ Fenster

**Was:** Implizite Wunschrichtung „alles vereinheitlichen“.  
**Warum zurück:** Audit verbietet **Wunscharchitektur**; keine Evidenz, dass Merge **ohne** großen Bruch möglich ist. **Zuerst** Kommunikation (IMP-004), dann entscheiden.  
**Wann sinnvoll:** Nur nach Produktentscheid und Kosten-Nutzen — **nicht** in der nächsten kleinen Runde.

---

## 6. Vollständige Neufassung aller Hilfe-Artikel

**Was:** Jeden `help/`-Markdown überarbeiten.  
**Warum zurück:** Gap-Report stellt **keine** flächendeckende „leere Kapitel“-Krise fest („nicht belastbar belegt“). **Zielgerichtet** genügt: Dual-UI, Legacy-Pfad, ggf. Verweis auf aktuelle Tests.  
**Wann sinnvoll:** Nach strukturellen Fixes, punktuell pro Workspace.

---

## 7. Neue Architektur-Guards / Test-Marker-Explosion

**Was:** Breite Erweiterung von `tests/architecture/` ohne konkreten Bug.  
**Warum zurück:** Audit betont bereits **gute** Guard-Nutzung; **größtes echtes Loch** ist **IMP-001**, nicht fehlende Metriken.  
**Wann sinnvoll:** Wenn nach IMP-001 neue Invarianten explizit werden.

---

## 8. Live-Ollama-Abhängigkeit für jeden PR erzwingen

**Was:** Alle Tests an echte Dienste binden.  
**Warum zurück:** `tests/README.md` trennt Live bewusst; würde **Kosten und Flakiness** erhöhen ohne Audit-Forderung.  
**Wann sinnvoll:** Gezielt für Release-Kandidaten, nicht für tägliche IMP-Runde.

---

## Kurzliste: „Definitiv nicht zuerst“

1. Generische **GUI-Kosmetik** ohne IMP-001/002/004  
2. **Große** Workbench-Realisierung vor IMP-004  
3. **Packaging** vor P0/P1  
4. **IMP-011** vor tragfähigem IMP-001-Mindestziel  
5. **Shell+Workbench technisch verschmelzen** ohne Entscheidung  

---

*Ende Deferred-Liste.*
