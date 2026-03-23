# Phase D – Lokale Modell-Artefakte (Scan & Sync)

## Neue Dateien

- `app/services/local_model_asset_classifier.py` – Pfad-/Suffix-basierte Klassifikation (`ModelAssetType`).
- `app/services/local_model_matcher.py` – konservative Registry-Zuordnung (`high` / `none`).
- `app/services/local_model_default_roots.py` – idempotente Standard-Registrierung von `~/ai` (`user_ai`).
- `app/services/local_model_scanner_service.py` – `LocalModelScannerService`, `LocalModelScanReport`.
- `tests/unit/test_local_model_scanner_service.py` – Scan-, Matching- und Robustheits-Tests.

## Geänderte Dateien

- `app/services/local_model_registry_service.py` – `upsert_asset_from_scan`, Hilfsfunktion `_merge_scan_into_metadata`.
- `app/services/model_usage_gui_service.py` – `run_local_inventory_scan()`.
- `app/gui/domains/control_center/panels/local_assets_panel.py` – Button „Speicherorte scannen“ (ruft nur die GUI-Service-Fassade auf).

## Unterstützte Asset-Typen (Klassifikation)

Entspricht `ModelAssetType`: `gguf`, `safetensors`, `tokenizer`, `modelfile`, `adapter`, `lora`, `config`, `directory`, `weights`, `other` (heuristisch über Suffixe und Dateinamen-Hinweise).

Zusätzlich werden **Verzeichnisse** als `directory` erfasst, die direktes Elternverzeichnis einer Datei der Typen `gguf` / `safetensors` / `weights` sind (ohne den Storage-Root selbst doppelt zu erfassen).

## Scan- und Matching-Regeln

- Es werden nur Roots gescannt mit `is_enabled` und `scan_enabled`.
- Dateisystem: `os.walk(..., followlinks=False)`; gespeicherte Pfade über `LocalModelRegistryService.normalize_absolute_path` (inkl. `resolve()`), damit Einträge stabil und symlink-sicher referenzierbar sind.
- **Matching:** exakter Pfadsegment-Treffer gegen Registry-IDs, exakter Dateiname (stem), oder genau eine ID der Form `stem:…`. Case-insensitive nur, wenn genau eine Registry-ID passt. Keine Fuzzy-Namen.
- **`model_id` setzen** nur bei `match_confidence == "high"`. Bestehende, nicht leere `model_id` werden bei Scans **nicht** überschrieben (`upsert_asset_from_scan`).
- Scan-Metadaten landen unter `metadata_json.scan` (Zeitstempel, letzte Confidence, letzter Vorschlag).

## Missing / Unavailable

- Nach dem Lauf: alle `ModelAsset` mit `storage_root_id` dieses Roots, deren `path_absolute` nicht mehr in der „gesehenen“ Menge liegt: `is_available = False`, `last_seen_at` wird gesetzt. **Keine** Zeilenlöschung.

## Default-Strategie für `~/ai`

- `ensure_user_ai_default_root(session)`: legt einen Root mit Name `user_ai`, Pfad `~/ai` (Home-Expansion), `scan_enabled=True`, `is_read_only=True` an, sofern dieser Pfad noch nicht existiert und der Name nicht kollidiert.
- `scan_all_enabled_roots(..., ensure_default_user_ai_root=True)` ruft das vor dem Scan auf (Standard in `run_local_inventory_scan`).

## Bewusst offen / Grenzen

- Keine Inhalts-Hashes (außer spätere explizite Strategie); Checksums bleiben unberührt.
- Keine semantische Modellordner-Erkennung jenseits der beschriebenen Heuristiken.
- Sehr große Bäume: Abbruch nach `max_entries` (Standard 200 000) mit Eintrag in `report.errors`.
- `scan_all_enabled_roots` summiert `unassigned_count` je Root; für globale Statistiken über alle Assets ist die GUI-Liste weiterhin maßgeblich.
