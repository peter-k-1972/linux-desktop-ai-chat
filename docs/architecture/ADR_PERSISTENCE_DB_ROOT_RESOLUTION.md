# ADR: Auflösung von Repo-Root und Default-DB-URL für `app.persistence`

| Feld | Inhalt |
|------|--------|
| **Status** | Akzeptiert |
| **Datum** | 2026-03-31 |
| **Kontext** | Vorbereitung physischer Split [`PACKAGE_PERSISTENCE_PHYSICAL_SPLIT.md`](PACKAGE_PERSISTENCE_PHYSICAL_SPLIT.md) |
| **Geltungsbereich** | Default-Pfad für SQLite, wenn `LINUX_DESKTOP_CHAT_DATABASE_URL` **nicht** gesetzt ist — ausschließlich `app.persistence.session.get_database_url()` (bzw. direkte Nachfolger desselben Vertrags). |

---

## 1. Problem

### Ist-Zustand

- `get_database_url()` nutzt nach leerem Env-Override `Path(__file__).resolve().parents[2]` als „Repo-Root“ und setzt die Default-URL auf `sqlite:///<root>/chat_history.db`.
- Das koppelt die Semantik an die **feste Tiefe** von `session.py` im Host-Baum (`app/persistence/session.py` → zwei Ebenen über `persistence` = Monorepo-Root).

### Konflikt mit physischem Split

- Nach Verlegung nach `linux-desktop-chat-persistence/src/app/persistence/session.py` wäre `parents[2]` typischerweise das Verzeichnis **`src/`**, nicht der Monorepo-Root.
- Folge: **stille** falsche Default-URL (SQLite unter `src/` oder Wheel-nahen Pfaden), abweichend von Alembic-/Entwickler-Erwartung und dem Runbook-Ziel „keine unbeabsichtigte Verlagerung“.

---

## 2. Ziele

| # | Ziel |
|---|------|
| G1 | **`LINUX_DESKTOP_CHAT_DATABASE_URL`** bleibt **oberste Priorität** (leer nach `strip` = weiter mit Default-Logik). |
| G2 | **Regulärer Host-Lauf** am Monorepo-Root mit `pip install -e .`: Default-Datei bleibt **`chat_history.db` im Monorepo-Root** (heutige fachliche Semantik). |
| G3 | Dieselbe Default-Semantik muss **unabhängig von der Installationslage** von `app.persistence` funktionieren (Host-Tree vs. eingebettetes Wheel unter `src/app/persistence/`). |
| G4 | **Keine stille** Verlagerung der SQLite-Datei in `src/`, Build- oder Site-Packages-Verzeichnisse. |

---

## 3. Nicht-Ziele

| # | Nicht-Ziel |
|---|------------|
| NZ1 | Kein neues, umfassendes Konfigurationssystem über Settings/Feature-Flags für diese Entscheidung. |
| NZ2 | Keine Alembic-Neuarchitektur; `alembic/env.py` darf weiter `get_database_url()` importieren, sofern der Vertrag dieses ADR eingehalten wird. |
| NZ3 | Keine Änderung der **fachlichen** Nutzung der DB (Tabellen, Services, ORM-Modelle). |
| NZ4 | Keine Garantie für beliebige **exotische** Installationslayouts ohne Env-Override (nur: definiertes, vorhersagbares Verhalten für den kanonischen Monorepo-Host und das künftige Wheel im selben Repo). |

---

## 4. Entscheidungsoptionen (Kurzüberblick)

| ID | Option | Kurzbeschreibung |
|----|--------|------------------|
| O1 | **Anker-basierte Root-Suche** | Von `Path(__file__)` aus nach oben wandern; Root = erstes Verzeichnis, in dem ein vereinbarter **Anker** liegt (z. B. `pyproject.toml` mit `[project]` `name = "linux-desktop-chat"`). |
| O2 | **Explizite Host-Konfiguration** | Default-URL wird aus einem zentralen Host-Modul (z. B. `app.core…`) gespeist; `app.persistence` importiert dieses Modul. |
| O3 | **Rein env-basierter Default** | Ohne Env **kein** filesystem-Default (Fehler, oder feste `:memory:`) — Produktivität nur mit gesetztem `LINUX_DESKTOP_CHAT_DATABASE_URL`. |
| O4 | **Dedizierte Env-Variable für Root** | Z. B. `LINUX_DESKTOP_CHAT_REPO_ROOT`; Default-DB = `<root>/chat_history.db`. |

---

## 5. Bewertung der Optionen

| Option | Vorteile | Nachteile | Host / Tests / CI / Wheel |
|--------|----------|-----------|---------------------------|
| **O1** | Kein zusätzlicher Pflicht-Env für Standard-Workflow; funktioniert gleich nach Split; keine neue Kopplung persistence → andere `app.*`-Domänen | Implementierung muss Anker-Parsing robust halten (Encoding, fehlende Datei) | **Host:** unverändertes Dev-Erlebnis. **Tests/CI:** bestehende Tests mit expliziter URL unverändert; Tests ohne Env weiterhin Root-DB wie heute. **Wheel:** gleiche Logik, solange Anker im Monorepo-Root liegt. |
| **O2** | Zentrale Sicht auf „App-Root“ möglich | Risiko **zyklischer Importe** oder unerwünschter Abhängigkeit persistence → core; Persistence-Schicht wird schwerer **eigenständig** testbar/installierbar | Wheel könnte core mitziehen müssen oder bricht ohne Host |
| **O3** | Minimaler Code | **Verletzt G2:** jeder lokale Lauf bräuchte Env oder akzeptiert anderes Verhalten | CI müsste überall URL setzen; Regression für Entwickler |
| **O4** | Einfach zu spezifizieren | Zweite Variable neben URL; ohne Setzen weiterhin **Root-Erkennung** nötig, sonst gleiches Problem wie heute | Redundant zu O1, wenn O1 ohnehin implementiert wird |

---

## 6. Entscheidung

**Gewählt: O1 — Anker-basierte Root-Suche** mit folgender verbindlicher Präzisierung:

1. **Priorität 1 (unverändert):** Wenn `LINUX_DESKTOP_CHAT_DATABASE_URL` nach `strip` nicht leer ist → diese URL zurückgeben.
2. **Priorität 2 (neu statt `parents[2]`):** Vom Verzeichnis von `session.py` aus **aufwärts** iterieren (Elternverzeichnisse bis zum Dateisystem-Root oder sinnvollem Abbruch, z. B. max. Tiefe dokumentiert im Code-Kommentar). Das **Monorepo-Root** ist das erste Verzeichnis, in dem **beides** zutrifft:
   - Es existiert eine Datei **`pyproject.toml`**, und
   - deren **`[project]`**-Sektion **`name = "linux-desktop-chat"`** (PEP 621, exakter String-Vergleich nach Normalisierung nur falls der Parser das ohnehin liefert — **Zielstring kanonisch: `linux-desktop-chat`**).

3. **Default-URL:** `sqlite:///<resolved_root>/chat_history.db` mit `resolved_root` als oben gefundenem Pfad (plattformgerechte URL-Kodierung beibehalten wie heute bei SQLite-Pfaden).

4. **Fehlerfall:** Wird kein Anker gefunden, ist das Verhalten **explizit** zu definieren im Implementierungs-PR: **empfohlen** — klare **Exception** mit Hinweis auf Setzen von `LINUX_DESKTOP_CHAT_DATABASE_URL` (kein stiller Fallback nach `src/`).

**O4** (`LINUX_DESKTOP_CHAT_REPO_ROOT`) wird **nicht** eingeführt; wer Root überschreiben will, nutzt die bestehende URL-Env.

---

## 7. Konsequenzen

### Was der Implementierungs-PR ändern darf

- Ersetzen der festen `parents[2]`-Logik in `get_database_url()` durch die in **§6** beschriebene Anker-Suche.
- Minimal notwendige Hilfsfunktion(en) **im selben Modul** oder in einem kleinen Submodule unter `app.persistence`, sofern Lesbarkeit das erfordert — **ohne** neue Abhängigkeit zu `app.core`, `app.services` oder GUI.
- Kurzer Modul-/Funktionskommentar, der auf **dieses ADR** verweist.
- Anpassung oder Ergänzung von Tests, die implizit von der alten Tiefe abhingen (falls vorhanden); bestehende Tests, die `LINUX_DESKTOP_CHAT_DATABASE_URL` setzen, bleiben unberührt.

### Was bewusst unverändert bleibt

- Semantik und Priorität von **`LINUX_DESKTOP_CHAT_DATABASE_URL`**.
- Zielpfad der Default-SQLite-Datei: **`chat_history.db` im Monorepo-Root** bei kanonischem Layout.
- Alembic-Verwendung von `get_database_url()` als Import — **kein** Pflicht-Refactor von `alembic/env.py`, solange der Vertrag von §6 eingehalten wird.
- Kein neues globales Konfigurationssystem (NZ1).

---

## 8. Restrisiken

- **Fremdcheckouts** ohne `pyproject.toml` am erwarteten Ort: ohne Env-Override → Exception (akzeptiert unter NZ4).
- **TOML-Parsing:** Abhängigkeit von Stdlib oder minimalem Parser; fehlerhafte `pyproject.toml` könnte die Suche stören — Implementierung soll defensiv sein und zur nächsten Elternstufe gehen, wenn die Datei nicht lesbar/kein gültiges PEP-621-Name-Feld ist.
- **Zukünftiger Umbenennung** des Projekts in `pyproject.toml`: Anker-String müsste mitgezogen werden (bewusste, seltene Änderung).

---

## Referenzen

- [`PACKAGE_PERSISTENCE_PHYSICAL_SPLIT.md`](PACKAGE_PERSISTENCE_PHYSICAL_SPLIT.md) — §6–§7 (Blocker und Vor-Schritt; dieses ADR präzisiert die Strategie **S2** dort).
