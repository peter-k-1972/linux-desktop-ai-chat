"""
Task Planner – analysiert User-Prompts und erzeugt Task-Graphen.

Nutzt optional ein LLM für intelligente Planung.
Fallback: Heuristik-basierte Zerlegung.
"""

import logging
import re
from typing import Any, Callable, Dict, List, Optional

from app.agents.task import Task
from app.agents.task_graph import TaskGraph

logger = logging.getLogger(__name__)

TASK_PLANNER_PROMPT = """Du bist ein Task-Planer für eine Agenten-Farm. Analysiere die Anfrage und zerlege sie in konkrete, delegierbare Aufgaben.

Anfrage: {query}

Antworte mit einer nummerierten Liste von Aufgaben. Jede Zeile: Nummer. Beschreibung [optional: tool_hint]
Tool-Hints (falls relevant): research, code, image, audio, video, thumbnail, comfyui_render, audio_pipeline, video_pipeline

Beispiel für "Erstelle ein Video über KI-Agenten":
1. Thema recherchieren (research)
2. Skript schreiben (code)
3. Voice generieren (audio)
4. Video rendern (video)
5. Thumbnail erstellen (thumbnail)

Aufgaben:"""


class TaskPlanner:
    """
    Plant Tasks aus User-Prompts.

    Kann ein LLM nutzen oder auf Heuristiken zurückfallen.
    """

    def __init__(
        self,
        llm_complete_fn: Optional[Callable[[str, List[Dict[str, str]]], Any]] = None,
        model_id: str = "qwen2.5:latest",
    ):
        """
        Args:
            llm_complete_fn: Async (model, messages) -> str. Wenn None, wird Heuristik genutzt.
            model_id: Modell für LLM-Planung
        """
        self._llm = llm_complete_fn
        self.model_id = model_id

    async def plan(self, user_prompt: str) -> TaskGraph:
        """
        Erzeugt einen Task-Graphen aus dem User-Prompt.

        Returns:
            TaskGraph mit allen geplanten Tasks
        """
        graph = TaskGraph()

        if self._llm:
            try:
                tasks_data = await self._plan_with_llm(user_prompt)
                prev_id = None
                for i, td in enumerate(tasks_data):
                    task = self._create_task_from_plan_item(td, i, user_prompt, prev_id)
                    if task:
                        graph.add_task(task)
                        prev_id = task.id
            except Exception as e:
                logger.warning("LLM-Planung fehlgeschlagen, Fallback auf Heuristik: %s", e)
                self._add_heuristic_tasks(graph, user_prompt)
        else:
            self._add_heuristic_tasks(graph, user_prompt)

        if not graph.get_all_tasks():
            # Fallback: ein einzelner Task mit dem gesamten Prompt
            graph.add_task(
                Task(
                    description=user_prompt[:200] + ("..." if len(user_prompt) > 200 else ""),
                    input={"prompt": user_prompt, "original_prompt": user_prompt},
                    priority=0,
                )
            )

        return graph

    async def _plan_with_llm(self, query: str) -> List[Dict[str, str]]:
        """Nutzt LLM zur Task-Planung."""
        prompt = TASK_PLANNER_PROMPT.format(query=query)
        messages = [{"role": "user", "content": prompt}]
        response = await self._llm(self.model_id, messages)
        return self._parse_llm_response(response or "", query)

    def _parse_llm_response(self, text: str, original_prompt: str) -> List[Dict[str, str]]:
        """Parst die LLM-Antwort in strukturierte Task-Daten."""
        tasks_data = []
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            # Nummerierung entfernen
            for prefix in (". ", ") ", "- "):
                for i in range(1, 30):
                    if line.lower().startswith(f"{i}{prefix}"):
                        line = line[len(f"{i}{prefix}"):].strip()
                        break
            if len(line) < 3:
                continue

            # Tool-Hint in Klammern extrahieren
            tool_hint = None
            match = re.search(r"\(([a-z_]+)\)\s*$", line, re.IGNORECASE)
            if match:
                tool_hint = match.group(1).lower()
                line = line[: match.start()].strip()

            tasks_data.append({
                "description": line,
                "tool_hint": tool_hint,
            })
        return tasks_data

    def _create_task_from_plan_item(
        self,
        item: Dict[str, str],
        index: int,
        original_prompt: str,
        prev_task_id: Optional[str] = None,
    ) -> Optional[Task]:
        """Erstellt einen Task aus einem Plan-Item."""
        desc = item.get("description", "").strip()
        if not desc:
            return None

        deps = [prev_task_id] if prev_task_id else []

        task = Task(
            description=desc,
            input={"prompt": desc, "original_prompt": original_prompt, "index": index},
            dependencies=deps,
            priority=100 - index,  # Frühere Tasks höhere Priorität
            tool_hint=item.get("tool_hint"),
        )
        return task

    def _add_heuristic_tasks(self, graph: TaskGraph, prompt: str) -> None:
        """Fügt Tasks basierend auf Heuristiken hinzu."""
        prompt_lower = prompt.lower()

        # Video-Produktion
        if any(kw in prompt_lower for kw in ["video", "videoproduktion", "animation"]):
            graph.add_task(
                Task(
                    description="Thema recherchieren",
                    input={"prompt": prompt, "original_prompt": prompt},
                    priority=90,
                    tool_hint="research",
                )
            )
            t2 = Task(
                description="Skript schreiben",
                input={"prompt": prompt, "original_prompt": prompt},
                priority=80,
                tool_hint="code",
            )
            t2.dependencies = [graph.get_all_tasks()[0].id] if graph.get_all_tasks() else []
            graph.add_task(t2)
            t3 = Task(
                description="Voice generieren",
                input={"prompt": prompt, "original_prompt": prompt},
                priority=70,
                tool_hint="audio",
            )
            t3.dependencies = [t2.id]
            graph.add_task(t3)
            t4 = Task(
                description="Video rendern",
                input={"prompt": prompt, "original_prompt": prompt},
                priority=60,
                tool_hint="video",
            )
            t4.dependencies = [t3.id]
            graph.add_task(t4)
            t5 = Task(
                description="Thumbnail erstellen",
                input={"prompt": prompt, "original_prompt": prompt},
                priority=50,
                tool_hint="thumbnail_generator",
            )
            t5.dependencies = [t4.id]
            graph.add_task(t5)
            return

        # Bild-Generierung
        if any(kw in prompt_lower for kw in ["bild", "image", "generiere", "zeichne"]):
            graph.add_task(
                Task(
                    description="Bild generieren",
                    input={"prompt": prompt, "original_prompt": prompt},
                    priority=80,
                    tool_hint="image",
                )
            )
            return

        # Code
        if any(kw in prompt_lower for kw in ["code", "programm", "script", "funktion"]):
            graph.add_task(
                Task(
                    description="Code erstellen",
                    input={"prompt": prompt, "original_prompt": prompt},
                    priority=80,
                    tool_hint="code",
                )
            )
            return

        # Recherche
        if any(kw in prompt_lower for kw in ["recherche", "research", "recherchiere", "informiere"]):
            graph.add_task(
                Task(
                    description="Recherche durchführen",
                    input={"prompt": prompt, "original_prompt": prompt},
                    priority=80,
                    tool_hint="research",
                )
            )
            return

        # Default: einzelner Task
        graph.add_task(
            Task(
                description=prompt[:200] + ("..." if len(prompt) > 200 else ""),
                input={"prompt": prompt, "original_prompt": prompt},
                priority=0,
            )
        )
