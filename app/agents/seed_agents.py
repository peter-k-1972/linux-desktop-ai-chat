"""
Seed Agents – Standard-Agenten für die Agentenorganisation.

Legt beim ersten Start oder auf Anfrage die vordefinierten Agenten an.
Standard: 19 Profile in 6 Departments (inkl. Project Butler). Erweiterbar für ComfyUI, Multimedia, Tools, Delegation.
"""

import logging
from typing import List, Optional

from app.agents.agent_profile import AgentProfile
from app.agents.agent_repository import AgentRepository
from app.agents.departments import Department
from app.core.models.roles import ModelRole

logger = logging.getLogger(__name__)


def _seed_profiles() -> List[AgentProfile]:
    """Liefert die Standard-Agentenprofile."""
    return [
        # --- PLANNING ---
        AgentProfile(
            name="Planner Agent",
            display_name="Planner Agent",
            slug="planner_agent",
            short_description="Planung und Projektmanagement",
            long_description="Zerlegt komplexe Aufgaben in Schritte, erstellt Pläne, priorisiert. "
            "Vorbereitet für Delegation und Task-Graphen.",
            department=Department.PLANNING.value,
            role="Planner",
            status="active",
            assigned_model="qwen2.5:latest",
            assigned_model_role=ModelRole.THINK.value,
            system_prompt="Du bist ein strukturierter Planer. Zerlege komplexe Aufgaben in konkrete Schritte.",
            capabilities=["summarize", "analysis"],
            tools=[],
            knowledge_spaces=[],
            tags=["planning", "strategy", "delegation"],
            priority=95,
        ),
        # --- RESEARCH ---
        AgentProfile(
            name="Critic Agent",
            display_name="Critic Agent",
            slug="critic_agent",
            short_description="Kritische Prüfung und Qualitätssicherung",
            long_description="Prüft Antworten auf Qualität, Logik und Vollständigkeit. "
            "Erkennt Lücken und Verbesserungspotenzial.",
            department=Department.RESEARCH.value,
            role="Critic",
            status="active",
            assigned_model="mistral:latest",
            assigned_model_role=ModelRole.FAST.value,
            system_prompt="Du prüfst Antworten kritisch. Erkenne Lücken, Widersprüche und Verbesserungspotenzial.",
            capabilities=["analysis"],
            tools=[],
            knowledge_spaces=[],
            tags=["critic", "quality"],
            priority=85,
        ),
        AgentProfile(
            name="Research Agent",
            display_name="Research Agent",
            slug="research_agent",
            short_description="Recherche und Faktenprüfung",
            long_description="Tiefgehende Recherche mit Planner, RAG und Critic-Pipeline. "
            "Zitiert Quellen, prüft Fakten.",
            department=Department.RESEARCH.value,
            role="Researcher",
            status="active",
            assigned_model="gpt-oss:latest",
            assigned_model_role=ModelRole.RESEARCH.value,
            system_prompt="Du bist ein sorgfältiger Researcher. Prüfe Fakten, zitiere Quellen.",
            capabilities=["research", "summarize", "rag", "analysis"],
            tools=["rag", "web_search"],
            knowledge_spaces=["default", "documentation"],
            tags=["research", "rag"],
            priority=90,
        ),
        AgentProfile(
            name="Knowledge Agent",
            display_name="Knowledge Agent",
            slug="knowledge_agent",
            short_description="Wissensmanagement und RAG",
            long_description="Nutzt indexierte Dokumente, beantwortet aus dem Knowledge Space. "
            "RAG-basierte Wissensabfragen.",
            department=Department.RESEARCH.value,
            role="Knowledge Manager",
            status="active",
            assigned_model="qwen2.5:latest",
            assigned_model_role=ModelRole.DEFAULT.value,
            system_prompt="Du beantwortest Fragen auf Basis des indexierten Wissens. Zitiere Quellen.",
            capabilities=["rag", "summarize", "analysis"],
            tools=["rag"],
            knowledge_spaces=["default", "documentation", "notes", "code"],
            tags=["knowledge", "rag"],
            priority=85,
        ),
        # --- DEVELOPMENT ---
        AgentProfile(
            name="Code Agent",
            display_name="Code Agent",
            slug="code_agent",
            short_description="Programmierung und Code-Review",
            long_description="Code schreiben, refaktorieren. Technischer Fokus. Sauberer, dokumentierter Code.",
            department=Department.DEVELOPMENT.value,
            role="Developer",
            status="active",
            assigned_model="qwen2.5-coder:7b",
            assigned_model_role=ModelRole.CODE.value,
            system_prompt="Du bist ein erfahrener Entwickler. Schreibe sauberen, dokumentierten Code.",
            capabilities=["code", "refactor", "documentation"],
            tools=["rag"],
            knowledge_spaces=["code", "documentation"],
            tags=["code", "developer"],
            priority=90,
        ),
        AgentProfile(
            name="Debugger Agent",
            display_name="Debugger Agent",
            slug="debugger_agent",
            short_description="Debugging und Fehleranalyse",
            long_description="Analysiert Fehler, findet Bugs, schlägt Fixes vor. Systematisches Debugging.",
            department=Department.DEVELOPMENT.value,
            role="Debugger",
            status="active",
            assigned_model="qwen2.5-coder:7b",
            assigned_model_role=ModelRole.CODE.value,
            system_prompt="Du analysierst Fehler systematisch. Finde die Ursache und schlage Fixes vor.",
            capabilities=["code", "debug", "analysis"],
            tools=["rag"],
            knowledge_spaces=["code", "documentation"],
            tags=["debug", "developer"],
            priority=85,
        ),
        AgentProfile(
            name="Documentation Agent",
            display_name="Documentation Agent",
            slug="documentation_agent",
            short_description="Dokumentation und technische Texte",
            long_description="Erstellt und verbessert Dokumentation, README, API-Docs, Kommentare.",
            department=Department.DEVELOPMENT.value,
            role="Technical Writer",
            status="active",
            assigned_model="qwen2.5:latest",
            assigned_model_role=ModelRole.DEFAULT.value,
            system_prompt="Du erstellst klare, strukturierte technische Dokumentation.",
            capabilities=["documentation", "summarize"],
            tools=["rag"],
            knowledge_spaces=["documentation", "code"],
            tags=["documentation", "technical-writing"],
            priority=80,
        ),
        AgentProfile(
            name="Script Agent",
            display_name="Script Agent",
            slug="script_agent",
            short_description="Skript-Generierung und Automatisierung",
            long_description="Generiert Shell-, Python- und andere Skripte. Automatisierungsaufgaben.",
            department=Department.DEVELOPMENT.value,
            role="Script Specialist",
            status="active",
            assigned_model="qwen2.5-coder:7b",
            assigned_model_role=ModelRole.CODE.value,
            system_prompt="Du erstellst funktionale Skripte für Automatisierung und Systemaufgaben.",
            capabilities=["code", "script_generation"],
            tools=[],
            knowledge_spaces=["code"],
            tags=["script", "automation"],
            priority=75,
        ),
        # --- MEDIA ---
        AgentProfile(
            name="Voice Agent",
            display_name="Voice Agent",
            slug="voice_agent",
            short_description="Sprachsynthese und Audio-Voice",
            long_description="Voice-Generierung, TTS, Audio-Pipelines. Vorbereitet für audio_pipeline.",
            department=Department.MEDIA.value,
            role="Voice Specialist",
            status="active",
            assigned_model="gpt-oss:latest",
            assigned_model_role=ModelRole.THINK.value,
            system_prompt="Du planst Voice- und Audio-Workflows: TTS, Transkription, Bearbeitung.",
            capabilities=["audio_generation"],
            tools=[],
            knowledge_spaces=["audio"],
            tags=["voice", "audio", "tts"],
            priority=70,
            media_pipeline_capabilities=["audio"],
            output_types=["audio"],
        ),
        AgentProfile(
            name="Image Agent",
            display_name="Image Agent",
            slug="image_agent",
            short_description="Bildgenerierung und -bearbeitung",
            long_description="Generiert und bearbeitet Bilder. Vorbereitet für ComfyUI/Stable Diffusion.",
            department=Department.MEDIA.value,
            role="Image Specialist",
            status="active",
            assigned_model="gpt-oss:latest",
            assigned_model_role=ModelRole.THINK.value,
            system_prompt="Du hilfst bei Bildgenerierung: Prompts formulieren, Parameter wählen.",
            capabilities=["image_generation"],
            tools=["comfyui"],
            knowledge_spaces=["image"],
            tags=["image", "generation"],
            priority=75,
            workflow_bindings=[],
            media_pipeline_capabilities=["image_generation"],
            output_types=["image"],
        ),
        AgentProfile(
            name="Video Agent",
            display_name="Video Agent",
            slug="video_agent",
            short_description="Videoproduktion und Animation",
            long_description="Video-Workflows, Animation, ComfyUI-Video-Module. Vorbereitet für video_pipeline.",
            department=Department.MEDIA.value,
            role="Video Specialist",
            status="active",
            assigned_model="gpt-oss:latest",
            assigned_model_role=ModelRole.THINK.value,
            system_prompt="Du planst Video-Produktionen: Szenen, Schnitt, Animation.",
            capabilities=["video_generation"],
            tools=["comfyui"],
            knowledge_spaces=["video"],
            tags=["video", "animation"],
            priority=70,
            media_pipeline_capabilities=["video"],
            output_types=["video"],
        ),
        AgentProfile(
            name="Music Agent",
            display_name="Music Agent",
            slug="music_agent",
            short_description="Musikproduktion und Komposition",
            long_description="Musik-Workflows, Komposition, Audio-Synthese. Vorbereitet für music_generation.",
            department=Department.MEDIA.value,
            role="Music Specialist",
            status="active",
            assigned_model="gpt-oss:latest",
            assigned_model_role=ModelRole.THINK.value,
            system_prompt="Du planst Musik-Projekte: Komposition, Arrangement, Produktion.",
            capabilities=["music_generation"],
            tools=[],
            knowledge_spaces=["music"],
            tags=["music", "composition"],
            priority=65,
            media_pipeline_capabilities=["music"],
            output_types=["audio"],
        ),
        # --- AUTOMATION ---
        AgentProfile(
            name="Workflow Agent",
            display_name="Workflow Agent",
            slug="workflow_agent",
            short_description="ComfyUI und Pipeline-Orchestrierung",
            long_description="Plant und koordiniert ComfyUI-Workflows, Medien-Pipelines. "
            "Vorbereitet für workflow_creation und Delegation.",
            department=Department.AUTOMATION.value,
            role="Workflow Coordinator",
            status="active",
            assigned_model="gpt-oss:latest",
            assigned_model_role=ModelRole.THINK.value,
            system_prompt="Du planst Medienprojekte: Bild, Video, Audio. Strukturiere Workflows.",
            capabilities=["workflow_creation"],
            tools=["comfyui"],
            knowledge_spaces=["media"],
            tags=["workflow", "comfyui"],
            priority=80,
            workflow_bindings=[],
            media_pipeline_capabilities=["planning"],
            output_types=["image", "video", "audio"],
        ),
        AgentProfile(
            name="Tool Agent",
            display_name="Tool Agent",
            slug="tool_agent",
            short_description="Tool-Ausführung und Integration",
            long_description="Führt Tools aus, integriert externe Befehle. Vorbereitet für Tool-Execution.",
            department=Department.AUTOMATION.value,
            role="Tool Specialist",
            status="active",
            assigned_model="qwen2.5:latest",
            assigned_model_role=ModelRole.DEFAULT.value,
            system_prompt="Du koordinierst Tool-Aufrufe und externe Befehle. Strukturiere Ausführungen.",
            capabilities=["workflow_creation"],
            tools=[],
            knowledge_spaces=[],
            tags=["tool", "execution"],
            priority=75,
            external_command_hooks=[],
        ),
        AgentProfile(
            name="Scheduler Agent",
            display_name="Scheduler Agent",
            slug="scheduler_agent",
            short_description="Zeitplanung und Task-Scheduling",
            long_description="Plant zeitgesteuerte Aufgaben, Cron-Jobs, wiederkehrende Tasks.",
            department=Department.AUTOMATION.value,
            role="Scheduler",
            status="active",
            assigned_model="qwen2.5:latest",
            assigned_model_role=ModelRole.DEFAULT.value,
            system_prompt="Du planst zeitgesteuerte und wiederkehrende Aufgaben.",
            capabilities=["workflow_creation"],
            tools=[],
            knowledge_spaces=[],
            tags=["scheduler", "automation"],
            priority=70,
        ),
        # --- SYSTEM ---
        AgentProfile(
            name="System Agent",
            display_name="System Agent",
            slug="system_agent",
            short_description="Systemadministration und Infrastruktur",
            long_description="Systemaufgaben, Infrastruktur, Konfiguration. Vorbereitet für system_monitoring.",
            department=Department.SYSTEM.value,
            role="System Admin",
            status="active",
            assigned_model="qwen2.5:latest",
            assigned_model_role=ModelRole.DEFAULT.value,
            system_prompt="Du unterstützt bei Systemadministration und Infrastruktur.",
            capabilities=["system_monitoring"],
            tools=[],
            knowledge_spaces=[],
            tags=["system", "admin"],
            priority=85,
        ),
        AgentProfile(
            name="Update Agent",
            display_name="Update Agent",
            slug="update_agent",
            short_description="Update-Management und Wartung",
            long_description="Verwaltet Updates, Patches, Wartungsaufgaben.",
            department=Department.SYSTEM.value,
            role="Update Manager",
            status="active",
            assigned_model="qwen2.5:latest",
            assigned_model_role=ModelRole.DEFAULT.value,
            system_prompt="Du planst und koordinierst Update- und Wartungsaufgaben.",
            capabilities=["update_management"],
            tools=[],
            knowledge_spaces=[],
            tags=["update", "maintenance"],
            priority=75,
        ),
        AgentProfile(
            name="Recovery Agent",
            display_name="Recovery Agent",
            slug="recovery_agent",
            short_description="Recovery und Wiederherstellung",
            long_description="Wiederherstellung nach Fehlern, Backup-Strategien, Disaster Recovery.",
            department=Department.SYSTEM.value,
            role="Recovery Specialist",
            status="active",
            assigned_model="qwen2.5:latest",
            assigned_model_role=ModelRole.THINK.value,
            system_prompt="Du unterstützt bei Recovery und Wiederherstellungsstrategien.",
            capabilities=["recovery"],
            tools=[],
            knowledge_spaces=[],
            tags=["recovery", "backup"],
            priority=80,
        ),
        AgentProfile(
            name="Monitor Agent",
            display_name="Monitor Agent",
            slug="monitor_agent",
            short_description="System-Monitoring und Überwachung",
            long_description="Überwacht Systeme, erkennt Anomalien, meldet Status.",
            department=Department.SYSTEM.value,
            role="Monitor",
            status="active",
            assigned_model="qwen2.5:latest",
            assigned_model_role=ModelRole.DEFAULT.value,
            system_prompt="Du analysierst Systemstatus und Monitoring-Daten.",
            capabilities=["system_monitoring", "analysis"],
            tools=[],
            knowledge_spaces=[],
            tags=["monitor", "observability"],
            priority=75,
        ),
        AgentProfile(
            id="agent.project.butler",
            name="Project Butler",
            display_name="Project Butler",
            slug="project_butler",
            short_description="Workflow-Orchestrierung (Klassifikation → passender Workflow)",
            long_description=(
                "Ordnet Nutzeranfragen per einfacher Heuristik einem Projekt-Workflow zu und startet ihn "
                "über die Workflow-Engine (kein Sonderpfad)."
            ),
            department=Department.AUTOMATION.value,
            role="Orchestrator",
            status="active",
            assigned_model="qwen2.5:latest",
            assigned_model_role=ModelRole.DEFAULT.value,
            system_prompt=(
                "Du bist die dokumentierte Rolle „Project Butler“: deine Logik liegt im "
                "ProjectButlerService (Klassifikation und WorkflowService.start_run), nicht in diesem Prompt."
            ),
            capabilities=["workflow_orchestration"],
            tools=[],
            knowledge_spaces=[],
            tags=["butler", "workflow", "orchestration"],
            priority=88,
        ),
    ]


def seed_agents(repository: Optional[AgentRepository] = None) -> int:
    """
    Legt die Standard-Agenten an, falls noch keine existieren.
    Returns: Anzahl neu angelegter Agenten.
    """
    repo = repository or AgentRepository()
    existing = repo.list_all()
    if existing:
        logger.info("Agenten bereits vorhanden, kein Seed nötig.")
        return 0
    count = 0
    for profile in _seed_profiles():
        try:
            repo.create(profile)
            count += 1
        except Exception as e:
            logger.warning("Seed Agent %s fehlgeschlagen: %s", profile.name, e)
    logger.info("Seed: %d Agenten angelegt.", count)
    return count


def ensure_seed_agents(repository: Optional[AgentRepository] = None) -> int:
    """
    Stellt sicher, dass alle Standard-Agenten existieren.
    Fehlende werden ergänzt (nach Slug-Prüfung).
    Wird beim ersten Start automatisch aufgerufen.
    Returns: Anzahl neu angelegter Agenten.
    """
    repo = repository or AgentRepository()
    existing_slugs = {p.slug for p in repo.list_all()}
    count = 0
    for profile in _seed_profiles():
        if profile.slug in existing_slugs:
            continue
        try:
            repo.create(profile)
            count += 1
            existing_slugs.add(profile.slug)
        except Exception as e:
            logger.warning("Seed Agent %s fehlgeschlagen: %s", profile.name, e)
    if count:
        logger.info("Seed: %d fehlende Agenten ergänzt.", count)
    return count
