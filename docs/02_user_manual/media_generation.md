# Medien-Generierung

## Übersicht

Die Medien-Generierung ist über das **design_system.json** konfigurierbar. Externe Pipelines werden über Befehlszeilen-Tools angesteuert.

## Konfigurierte Pipelines

| Modul | Befehl |
|-------|--------|
| Text-to-Image | `~/ai/pipeline/run_pipeline.py --module image` |
| Image-to-Animation | `~/ai/pipeline/run_pipeline.py --module animation` |
| Video-Production | `~/ai/pipeline/run_pipeline.py --module video` |

## Agenten mit Media-Capabilities

- **Image Agent**: Bildgenerierung, ComfyUI
- **Video Agent**: Video, Animation
- **Voice Agent**: TTS, Audio
- **Music Agent**: Musikproduktion
- **Workflow Agent**: Orchestrierung aller Media-Pipelines

## Nutzung

1. Passenden Agent wählen (z.B. Image Agent)
2. Anfrage formulieren (z.B. „Erstelle ein Bild von …“)
3. Agent generiert ggf. Prompts/Parameter für die Pipeline
4. Externe Pipeline wird aufgerufen (wenn integriert)

## Hinweis

Die vollständige Integration der Media-Pipelines ist in Entwicklung. Die Pfade in `design_system.json` können angepasst werden.
