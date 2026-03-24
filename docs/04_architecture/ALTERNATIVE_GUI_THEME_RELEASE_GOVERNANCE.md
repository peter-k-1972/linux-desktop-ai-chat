# Freigabe-, Versions- und QA-Governance für alternative GUIs / Themes (Linux Desktop Chat)

**Rolle:** Release-Governance, QA-Gates, Kompatibilitätsnachweis — **ohne** Implementierungsvorgaben oder QML-Code.

**Geltungsbereich:** Alternative GUI-Varianten (insbesondere die **QML Library GUI**), parallel zur **bestehenden Haupt-GUI**. Keine stillschweigende Weitergeltung von Freigaben bei Änderungen an Theme, Bridge, UI-Contracts/Ports, Backend oder Routing.

**Leitentscheidung:** Ein **Theme** ist ein **versioniertes Lieferobjekt** mit **expliziter Kompatibilitätsdeklaration** gegen App-, Backend-, Contract- und Bridge-Versionen. Freigaben sind **auditierbar** (Manifest + Matrix + QA-Nachweis + Approval-Log) und **re-test-fähig** (klare Trigger für Re-QA).

---

## 1. RELEASE OBJECT MODEL

### 1.1 Freigaberelevante Objekte

| Objekt | Definition (Linux Desktop Chat) | Freigabepflicht |
|--------|----------------------------------|-----------------|
| **Theme (gesamt)** | Die installierbare **alternative GUI**-Einheit: gebündelte QML-/Asset-/Konfigurationslieferung unter einer `theme_id`, inkl. Manifest und Kompatibilitätsdeklaration. | **Ja** — ohne Gesamt-Freigabe keine Installation als Alternativ-GUI. |
| **Foundation** | Gemeinsame UI-Bausteine, Layout-Tokens, Basiskomponenten (Repo-Anker: `qml/foundation/`). | **Ja** — **Pflicht-Teilversion** `foundation_version` im Manifest. |
| **Shell** | Globale Chrome: Navigation, Stage-Host, Overlay-Host, Shell-State (Repo-Anker: `qml/shell/`, Shell-Navigation). | **Ja** — **Pflicht-Teilversion** `shell_version`. |
| **Bridge** | Python↔QML-Grenze: Fassaden, Property-/Signal-Verträge, erlaubte Aufrufe (Repo-Anker: z. B. `shell_bridge_facade`, Runtime-Bridge). | **Ja** — **Pflicht-Teilversion** `bridge_version`. |
| **Domain-Stages** | Je Hauptbühne ein Stage-Paket (Chat, Projects, Prompt Studio, Workflows, Agents, Deployment, Settings — gemäß Navigations-/Stage-Katalog). | **Ja** — **Pflicht** als Map `domain_versions` (pro `domain_id` eine Version). |

### 1.2 Verpflichtende Teilversionen

Für jede **Theme-Release-Zeile** (siehe §2) müssen folgende Versionen **explizit** gesetzt und in der **Kompatibilitätsmatrix** (§3, §10) nachvollziehbar sein:

- `theme_version` (Gesamt)
- `foundation_version`
- `shell_version`
- `bridge_version`
- `domain_versions` (**alle** in der Theme-Navigation registrierten Domänen; keine „stille“ Halbintegration)

**Begründung:** Foundation/Shell/Bridge sind **Querschnitt** — ein Patch in der Bridge kann alle Stages bricht; Domänen sind **fachliche Oberflächen** — isolierte UX-/Contract-Abweichungen müssen separat versioniert und testbar sein.

### 1.3 Optionale Unterobjekte (empfohlen, nicht zwingend für minimales Gate)

| Objekt | Nutzen | Standard |
|--------|--------|----------|
| **Theme-Paket (visuell)** | Reine Token/QML-`themes/`-Schicht ohne Logikänderung | Version als `theme_pack_version` optional; wenn vorhanden, **PATCH-only** Änderungen dürfen ohne Bridge-Bump nur mit Matrix-Update erfolgen, wenn §9 es erlaubt. |
| **Lokalisierung / Copy-Deck** | Texte, Fehlermeldungen | Empfohlen `content_locale_version`; bei Contract-relevanten Strings: MINOR/Major-Regeln aus §2 anwenden. |

---

## 2. VERSIONING MODEL

### 2.1 Gewähltes Schema: SemVer für Gesamt und Teile

**Entscheidung:** Überall **Semantic Versioning `MAJOR.MINOR.PATCH`** (ohne Build-Metadaten in der Vergleichslogik; Build-/Git-Hashes nur als **Zusatzfelder** für Audit).

| Ebene | Feld | Bedeutung |
|-------|------|-----------|
| Gesamt | `theme_version` | Auslieferbare Theme-Zeile für die alternative GUI. |
| Teile | `foundation_version`, `shell_version`, `bridge_version` | Unabhängig bumpbar, müssen aber zum Gesamt-Release konsistent dokumentiert sein. |
| Domänen | `domain_versions[<domain_id>]` | Pro Stage eigene SemVer. |

**Warum SemVer (und nicht CalVer):** Themes müssen **Kompatibilitätsranges** gegen App/Backend/Contracts sauber kommunizieren; SemVer ist für **API-/Contract-Nähe** (Bridge, Ports) und für **Abhängigkeitsmatcher** in Registry/Matrix üblich und maschinenlesbar.

### 2.2 Wann steigt MAJOR / MINOR / PATCH?

| Änderung | Theme gesamt | Foundation | Shell | Bridge | Domain-Stage |
|----------|--------------|------------|-------|--------|--------------|
| Breaking Change am **öffentlichen** Bridge- oder Port/Contract (Signatur, Semantik, Fehlerverhalten) | **MAJOR** | ggf. **MAJOR** wenn APIs davon betroffen | ggf. **MAJOR** wenn Navigations-/Routing-Vertrag bricht | **MAJOR** | **MAJOR** wenn Stage den neuen Contract **zwingend** bricht |
| Neue **sichtbare** Fähigkeit, neue Route/Stage, neue Navigationsposition, neue **minor** Port-Erweiterung (rückwärtskompatibel) | **MINOR** | **MINOR** | **MINOR** | **MINOR** | **MINOR** |
| Bugfix, visuelle Korrektur, Performance, **ohne** Contract-/Routing-Änderung | **PATCH** | **PATCH** | **PATCH** | **PATCH** | **PATCH** |
| Reines **Asset/Token**-Tuning ohne Logik | **PATCH** (Gesamt) | **PATCH** oder `theme_pack`-Bump | meist **PATCH** | **PATCH** (typisch unverändert) | **PATCH** |

### 2.3 Was gilt als „reiner Patch-Fix“ vs. „neue Freigabe erzwingend“?

**Reine Patch-Fixes** (PATCH, Re-QA gemäß §6 abhängig von Betroffenheit):

- Korrektur von UI-Bugs ohne Änderung der Bridge-API oder Port-Aufrufreihenfolge.
- Kontrast/Spacing nach WCAG-Ziel **innerhalb** der deklarierten Design-Tokens.
- Absturzfix **ohne** geänderte Grenzverträge.

**Neue Freigabe / erweiterter Nachweis** (mindestens **neuer QA-Lauf**; oft **MINOR/MAJOR** + Matrix-Update):

- Jede Änderung an **Bridge**, **Ports/Contracts**, **Routing-Wahrheit** (inkl. Default-Domain, Stage-Ladeort).
- Entfernen oder Umbenennen einer `domain_id`.
- Änderung der **Kompatibilitätsdeklaration** (Ranges) — auch wenn Code „nur“ angepasst wurde.

**Hard rule:** Ein Bump von **MAJOR** bei Bridge oder Contracts erzwingt **immer** Update der **Kompatibilitätsmatrix** und **kein** „weitergelten“ der alten Freigabe (§9).

---

## 3. COMPATIBILITY MODEL

### 3.1 Kompatibilitätsdimensionen

| Dimension | Beispiel-Artefakt / Quelle | Rolle |
|-----------|----------------------------|--------|
| **Theme-Version** | `theme_version` + Teilversionen | Was der Kunde installiert. |
| **App-Version** | Hauptprogramm-Release (SemVer) | Prozessstart, Feature-Flags, Registry, Einstellungen. |
| **Backend-/Service-Version** | Orchestrierung, Chat-Service, DB-Schema-Version (sofern exponiert) | Daten- und Verhaltenskompatibilität der Stages. |
| **UI-Contracts-/Ports-Version** | Versionierte Port-/Contract-Pakete (z. B. `ui_contracts_version`) | Stabile Grenze zwischen GUI und Anwendungskern. |
| **Bridge-Version** | `bridge_version` im Theme | Übersetzungsschicht QML↔Python. |

### 3.2 Wann gilt ein Theme als „kompatibel“?

**Definition (operational):** Ein Theme `T` ist **kompatibel** mit einer Laufzeit-Konfiguration `(A, B, C, Br)` (App, Backend, Contracts, Bridge **der App-Seite**) **genau dann**, wenn:

1. `compatible_app_versions` von `T` den Wert `A` **eindeutig** erfüllt (SemVer-Range, siehe §4).
2. `compatible_backend_versions` den Wert `B` erfüllt **oder** explizit `B` in einer **Testmatrix-Zeile** als verifiziert geführt ist (§10).
3. `compatible_contract_versions` den Wert `C` erfüllt.
4. Die **Bridge-Version des Themes** `T.bridge_version` ist mit der **vom App-Stack erwarteten Bridge-Schnittstelle** vereinbart: entweder **exakt** der vom App-Release unterstützte Satz, oder durch eine **gemeinsam signierte** Kompatibilitätsaussage in der Matrix (kein stillschweigendes „passt schon“).

**Gegenseitige Protokollierung (Pflicht):**

| Seite | Artefakt | Inhalt |
|-------|----------|--------|
| Theme | Theme-Manifest (§4) | Deklariert kompatible App/Backend/Contract/Bridge. |
| App | **GUI-Registry** / Release-Bundle | Listet **zugelassene** `theme_id` + erlaubte `theme_version`-Ranges + **gegen welche** `ui_contracts_version` / `bridge_interface_version` getestet wurde. |

**Konfliktregel:** Stimmen Manifest und App-Registry **nicht** überein, ist das Theme **nicht installierbar** (Fail-Closed).

### 3.3 Kompatibilitätsmatrix (logisch)

Die Matrix ist die **kanonische** Übersicht aller **nachgewiesenen** Kombinationen (nicht nur theoretische Ranges).

| theme_id | theme_version | app_version (getestet) | backend_version (getestet) | contract_version | bridge_version (Theme) | bridge_interface_version (App) | QA-Run-ID | Ergebnis |
|----------|---------------|------------------------|----------------------------|------------------|-------------------------|---------------------------------|-----------|----------|
| `qml_library` | 1.2.0 | 0.9.3 | backend-bundle `2025-03-01` | `ui_contracts@2.1.0` | 1.2.0 | `bridge_iface@1.2.0` | QA-2025-031 | pass |

**Re-Test-Pflicht (kurz):**

| Ereignis | Re-Test |
|----------|---------|
| App **MINOR** innerhalb deklarierter Range | **Smoke + Routing** mindestens; voller Gate nur wenn Shared Code in Ports berührt wurde. |
| App **PATCH** | **Smoke**; voller Gate bei Bridge/Contract-Änderungen in der App. |
| App **MAJOR** | **Voller QA-Gate** für das Theme. |
| Backend **schema-breaking** oder **MAJOR** | **Voller Gate** für alle Stages mit Persistenz/I/O. |
| Contracts **MAJOR** | **Voller Gate** + **MAJOR**-Theme-Bump falls nötig. |
| Bridge **MAJOR** | **Voller Gate** + Matrix-Update. |

---

## 4. THEME MANIFEST MODEL

### 4.1 Manifest-Datei

**Dateiname (Konvention):** `theme_manifest.json` (oder `theme_manifest.yaml`) **im Theme-Root**.

### 4.2 Pflichtfelder (Schema)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `theme_id` | string | Stabile ID, z. B. `qml_library`. |
| `theme_name` | string | Anzeigename. |
| `theme_version` | semver | Gesamtversion der Theme-Lieferung. |
| `release_status` | enum | Siehe Statuskette §7 (Manifest spiegelt **aktuellen** Stand). |
| `foundation_version` | semver | Siehe §1. |
| `shell_version` | semver | Siehe §1. |
| `bridge_version` | semver | Theme-Seite der Bridge-Implementierung. |
| `domain_versions` | object | Map: `domain_id` → semver (alle registrierten Domains). |
| `compatible_app_versions` | string (SemVer range) | z. B. `>=0.9.3 <0.10.0`. |
| `compatible_backend_versions` | string oder strukturiert | Range **oder** Liste explizit freigegebener Backend-Build-IDs. |
| `compatible_contract_versions` | string (SemVer range) | Bezug auf `ui_contracts` / Port-Paket-Version. |
| `bridge_interface_requirement` | string | Erwartete **App-Bridge-Schnittstellenversion** (symmetrisch zur App-Registry). |
| `qa_status` | enum | `not_run` \| `in_progress` \| `pass` \| `pass_with_findings` \| `blocked` \| `failed`. |
| `qa_report_ref` | URI / Pfad | Verweis auf archivierten QA-Bericht (Build-ID, Datum). |
| `approval_ref` | URI / Pfad | Verweis auf Approval-Log-Eintrag (§7). |
| `integrity` | object | **Empfohlen:** Hash über Lieferumfang (Manifest + relevante Pakete). |

### 4.3 Beispiel (illustrativ, JSON)

```json
{
  "theme_id": "qml_library",
  "theme_name": "QML Library GUI",
  "theme_version": "1.2.0",
  "release_status": "qa_passed",
  "foundation_version": "1.2.0",
  "shell_version": "1.1.5",
  "bridge_version": "1.2.0",
  "domain_versions": {
    "chat": "1.2.0",
    "projects": "1.1.0",
    "prompt_studio": "1.2.0",
    "workflows": "1.0.4",
    "agent_tasks": "1.0.2",
    "deployment": "1.0.1",
    "settings": "1.1.0"
  },
  "compatible_app_versions": ">=0.9.3 <0.10.0",
  "compatible_backend_versions": ">=2025-03-01",
  "compatible_contract_versions": ">=2.1.0 <3.0.0",
  "bridge_interface_requirement": "1.2.0",
  "qa_status": "pass_with_findings",
  "qa_report_ref": "docs/qa/reports/THEME_qml_library_1.2.0_QA.md",
  "approval_ref": "docs/governance/approval_log/THEME_qml_library_1.2.0.md"
}
```

---

## 5. QA GATE MODEL

### 5.1 Gate-Philosophie

Ein **QA-Gate** ist **kein** Einzeltest, sondern eine **abnahmefähige** Checkliste mit **einheitlichen Exit-Status** und **Nachweispflicht**. Jedes Gate wird **pro Theme-Version** (und bei Re-Test gemäß §3.3) ausgeführt.

### 5.2 Prüfblöcke (Pflicht)

| Block | Inhalt / Fragestellung | Minimalnachweis |
|-------|------------------------|-----------------|
| **Architektur** | Einhaltung der Schichten: Foundation/Shell/Domains/Bridge; keine verbotenen Abhängigkeiten; Ports als einzige Service-Kante wo vorgesehen. | Architektur-Review-Checkliste + ggf. statische Guards (Referenz in QA-Bericht). |
| **Startbarkeit** | Kaltstart, Reload, Fehlerpfade (fehlende Ressource, fehlende Berechtigung). | Protokoll Screenshots/Logs, Zeitbudget. |
| **Routing / Navigation** | Rail ↔ `activeDomain` ↔ Stage-Loader: kein „geheimer“ Screen-Stack; Default-Domain korrekt. | Testfälle mit Domain-IDs aus dem Katalog. |
| **Theme- / Token-Konsistenz** | Farben, Typo, Spacing, Dark/Light; keine „harten“ Abweichungen ohne Token. | Visuelle Stichprobe + Token-Liste. |
| **Bridge-Grenzen** | Nur dokumentierte API; keine synchronen Langläufer in UI-Thread; Fehler semantisch korrekt. | Grenz-Testfälle + Negativtests. |
| **Domänenstatus** | Jede registrierte Stage: laden, leerer Zustand, typischer Happy Path, Degradation ohne Crash. | Matrix „Domain × Szenario“. |
| **UX / Usability** | Orientierung, Rückmeldungen, Fehlermeldungen verständlich; konsistente Interaktionsmuster. | Kurz-UX-Review (Heuristik). |
| **Accessibility / Kontrast** | Tastaturpfade wo vorgesehen; Fokus; Kontrast gegen definiertes Ziel. | A11y-Checkliste + Stichproben. |
| **Installation als Alternativ-GUI** | Registry-Eintrag, Umschalten, Rollback auf Standard-GUI, erneutes Umschalten. | End-to-End-Szenario (§8). |

### 5.3 Ergebnisstatus (Gate-Gesamt und pro Block)

| Status | Bedeutung | Freigabe |
|--------|-----------|----------|
| **pass** | Alle Pflichtkriterien erfüllt, keine relevanten Findings. | Erlaubt Übergang zu **Approval** (§7). |
| **pass_with_findings** | Keine Blocker; Findings sind ** dokumentiert** und als **nicht freigaberelevant** klassifiziert (§6). | Erlaubt Approval nur mit **explizitem** Finding-Acceptance-Eintrag. |
| **blocked** | Unklarer Zustand, fehlende Nachweise, Umgebung nicht reproduzierbar. | **Kein** Approval bis aufgelöst. |
| **failed** | Mindestens ein Pflichtkriterium verletzt oder freigaberelevantes Finding. | **Kein** Approval; Remediation (§6). |

**Regel:** „pass_with_findings“ darf **nicht** für Themen genutzt werden, die **Sicherheit, Datenintegrität, Crash- oder Contract-Brüche** betreffen — das ist **failed**.

---

## 6. BLOCKER / REMEDIATION WORKFLOW

### 6.1 Erfassung

- Jeder Blocker erhält **ID**, **Schwere** (S0–S3), **Betroffene Schicht** (Foundation/Shell/Bridge/Domain), **Repro-Schritte**, **Log-Auszug**, **Owner**.
- Blocker landen im **Release-Blocker-Backlog** (verlinkt aus QA-Bericht).

| Schwere | Beispiel |
|---------|----------|
| **S0** | Datenverlust, sicherheitsrelevant |
| **S1** | Crash / nicht startfähig / Contract-Bruch |
| **S2** | Wesentliche Funktion defekt |
| **S3** | Kosmetik / vereinzelte UX, kein Crash |

### 6.2 Priorisierung

1. S0/S1 vor allem anderen.  
2. Bridge/Contract/Routing vor rein visuellen Themen.  
3. Domänen mit hoher Nutzungsfrequenz (Chat, Projects, Settings) vor Rand-Stages.

### 6.3 Remediation & Re-QA

| Änderung nach failed/blocked | Re-QA-Umfang |
|------------------------------|--------------|
| Fix nur in **einer** Domain, keine Shared-Änderung | **Domain-Regression** + **Smoke** + betroffene Blöcke. |
| Änderung an **Shell/Routing** | **Routing-Block** + **Architektur** + Smoke + alle Domains **Smoke**. |
| Änderung an **Bridge** | **Bridge-Block** + **vollständiger** Gate (alle Blöcke). |
| Änderung an **Contracts/Ports** | **Voller Gate** + Matrix-Update (§3). |

### 6.4 Freigaberelevanz von Findings

| Finding-Typ | Standard |
|-------------|----------|
| Sicherheit, Daten, Crash, Contract | **Freigaberelevant** — muss behoben oder **MAJOR**-Block mit Ausnahme-Prozess. |
| A11y unterhalb des vereinbarten Ziels | **Freigaberelevant**, wenn im QA-Plan als Pflicht markiert; sonst **Backlog** mit Datum. |
| Kosmetik, Microcopy | **Nicht freigaberelevant**, wenn dokumentiert und productseitig akzeptiert. |

---

## 7. APPROVAL WORKFLOW

### 7.1 Statuskette

```
draft → candidate → qa_failed | qa_blocked → qa_passed → approved → installed_as_alternative_gui → deprecated
```

| Status | Bedeutung |
|--------|-----------|
| **draft** | Entwicklung, Manifest unvollständig. |
| **candidate** | Build erstellt, QA kann starten; Manifest vollständig. |
| **qa_failed** | Gate **failed**; kein Produktiv-Einsatz. |
| **qa_blocked** | Unklar/unvollständig; QA stoppt bis Umgebung/Repro geklärt. |
| **qa_passed** | Gate **pass** oder **pass_with_findings** mit dokumentiertem Finding-Acceptance. |
| **approved** | Rollenfreigabe (siehe unten) liegt vor; Matrix und Registry werden aktualisiert. |
| **installed_as_alternative_gui** | Im Produktpaket als wählbare GUI registriert (§8). |
| **deprecated** | Keine neuen Installationen; bestehende Nutzung nur bis End-of-Life-Date. |

**Hinweis:** `qa_failed` und `qa_blocked` sind **keine** linearen Zwischenstufen von `candidate` — sie sind **Ergebniszustände**, aus denen nach Fix erneut `candidate` oder direkt neu bewertet wird (Prozessführung: Team-Convention, im Approval-Log festhalten).

### 7.2 Erforderliche Nachweise für Freigabe (`approved`)

| Nachweis | Verantwortlich |
|----------|----------------|
| Archivierter **QA-Bericht** mit Gate-Status pro Block | QA |
| **Kompatibilitätsmatrix-Zeile(n)** für die freigegebene Kombination | Release Engineering |
| **Manifest** mit finalen Versionen und Ranges | Theme Owner |
| **Approval-Log-Eintrag** (Datum, Versionen, Rollen, Findings-Acceptance) | Product Owner + Tech Lead / Architect |
| **Diff zum vorherigen approved Theme** (Changelog) | Theme Owner |
| **Registry-Patch** (App-seitig: erlaubte `theme_id` + Version) | Release Engineering |

**Vier-Augen-Prinzip:** Mindestens **zwei** disjunkte Rollen (z. B. QA + Product/Tech) für `approved`.

---

## 8. INSTALLATION AS ALTERNATIVE GUI

### 8.1 Ziele

- **Keine** harte Ersetzung der Haupt-GUI.  
- **Paralleler** Lebenszyklus: Standard-GUI bleibt Default bis explizit umgestellt.  
- **Rollback** jederzeit auf Standard-GUI.

### 8.2 Mechanismus (konzeptionell)

| Komponente | Zweck |
|------------|--------|
| **GUI-Registry** | Zentrale Liste registrierter GUIs: `gui_id`, Entrypoint, `theme_id`, unterstützte App-Versionen, Pflicht-Contract-Version. |
| **Registrierter Entrypoint** | Startpfad der alternativen GUI (z. B. separates Runtime-Modul oder Theme-Loader), **ohne** Umverdrahtung der Standard-GUI-Binärdatei. |
| **Umschaltbarkeit** | Nutzer- oder Admin-Einstellung: „Aktive GUI“ = `default` \| `qml_library` (etc.); Validierung gegen Registry + Manifest. |
| **Rollback** | Bei Fehlschlag oder Inkompatibilität: Fallback auf `default` **und** Hinweis im Log; keine stille Endlosschleife. |

### 8.3 Validierung zur Laufzeit

1. App-Version ∈ `compatible_app_versions` (Theme-Manifest).  
2. Theme-Eintrag ∈ App-Registry für diese App-Version.  
3. `ui_contracts_version` der App ∈ `compatible_contract_versions`.  
4. `bridge_interface_requirement` des Themes matcht die App — sonst **kein Start** der alternativen GUI.

### 8.4 Paketierung

- Theme als **add-on** Paket (oder klar abgegrenztes Untermodul), das **zusammen** mit einer **bestimmten** App-Minor getestet wurde.  
- **Kein** Mischen von Theme-Versionen über App-Grenzen hinweg ohne neue Matrix-Zeile.

---

## 9. CHANGE IMPACT RULES

### 9.1 Sofort Re-QA (mindestens)

| Änderung | Auswirkung |
|----------|------------|
| **Bridge** (öffentliche API, Threading, Fehlercodes) | Voller QA-Gate; oft MINOR/MAJOR; Matrix + Manifest. |
| **UI-Contracts / Ports** (Methodensignaturen, Events, DTOs) | Voller Gate; Contract-Bump; Theme-Kompatibilität prüfen. |
| **Routing / Shell-State** (Default-Domain, Loader-Pfade) | Routing-Block + Domain-Smoke für alle; Manifest wenn Nav-Katalog ändert. |
| **Foundation** (verwendete öffentliche Komponenten-API von Domains) | Alle betroffenen Domains Re-Test; MINOR/PATCH je nach Bruch. |
| **Domain-Stage** fachliche I/O-Änderung | Domain-Regression + Bridge-Block-Stichprobe. |

### 9.2 Teilfreigaben

Wenn nur ein **Teil** des Themes geändert wird (z. B. eine Domain), darf die **Freigabe** trotzdem nur für den **Gesamt-Build** erfolgen, aber der **Nachweis** muss klar sagen:

- welche `domain_versions` sich geändert haben,  
- welche QA-Blöcke **voll** wiederholt wurden.

**Kein** „Teil-approved“ im Manifest ohne neue `theme_version`-Linie — optional kann ein **Kompatibilitäts-Addendum** die Matrix erweitern, aber das **Manifest** bleibt pro Release-Zeile konsistent.

### 9.3 Manifest- und Matrix-Pflicht

| Änderung | Manifest | Matrix | Changelog |
|----------|----------|--------|-----------|
| App-Minor-Range erweitert | Ja | Neue Testzeile | Ja |
| Backend breaking | Ja | Neue Testzeile | Ja |
| Nur Theme-PATCH visuell | Version bump | Referenz auf QA-Run | Ja |
| Bridge MAJOR | Ja | Ja | Ja |

### 9.4 Stillschweigende Weitergeltung

**Verboten.** Jede Änderung an Bridge, Contracts, Ports, Routing, Foundation oder Domain-Stages **invalidiert** die vorherige `approved`-Aussage, bis ein neuer Nachweis existiert.

---

## 10. REQUIRED FILES / REGISTRIES

| Artefakt | Zweck | Eigentümer |
|----------|-------|------------|
| **`theme_manifest.json`** | Kanonische Theme-Metadaten & Versionen | Theme Owner |
| **`THEME_COMPATIBILITY_MATRIX.md`** (oder maschinenlesbar `.yaml`) | Nachweis getesteter Kombinationen | Release Engineering |
| **`QA_GATE_ALTERNATIVE_GUI.md`** | Master-Checkliste aller Blöcke (§5) | QA Lead |
| **`approval_log/*.md`** | Unterschriebene Freigaben mit Verweisen | Product / Release |
| **`gui_registry.json`** (App-Bundle) | Erlaubte alternative GUIs & Entrypoints | App Platform |
| **`CHANGELOG_THEME_<theme_id>.md`** | User- und auditrelevante Änderungen | Theme Owner |
| **`qa/reports/THEME_<id>_<version>_QA.md`** | Archivierte Ergebnisse inkl. Anhängen | QA |

**Abgleich:** Bei jedem Release-Tag des Hauptprogramms muss die **Registry** und die **Matrix** zum Tag **committiert** oder **als Release-Asset** versioniert sein, damit externe Audits die **zulässigen** Themes rekonstruieren können.

---

## Anhang A — Abgrenzung Haupt-GUI vs. alternative QML-GUI

| Aspekt | Haupt-GUI | Alternative QML-GUI |
|--------|-----------|---------------------|
| Lebenszyklus | Standard, höchste Reifeerwartung | Theme-Zeile mit eigenem QA-Gate |
| Freigabe | Produktrelease | Theme-Release + Registry-Eintrag |
| Rollback | N/A (Default) | Immer möglich |

---

## Anhang B — Kurzbegründung der gewählten Einheit (SemVer + Matrix + Registry)

Für Linux Desktop Chat existiert bereits eine **komplexe** Desktop-Software mit **serviceseitigen** und **GUI-seitigen** Änderungsraten. **SemVer** für Theme und Teile erlaubt **maschinenlesbare** Kompatibilitätsentscheidungen; die **Matrix** erzwingt **nachvollziehbare** real getestete Kombinationen (nicht nur theoretische Ranges); die **GUI-Registry** auf App-Seite stellt **gegenseitige** Zustimmung sicher und verhindert **Fail-Open** bei Drift zwischen Manifest und Produkt.

---

*Dokumentversion: 1.0 — Governance-Konzept zur Ableitung von QA-/Freigabe-/Installationslogik.*
