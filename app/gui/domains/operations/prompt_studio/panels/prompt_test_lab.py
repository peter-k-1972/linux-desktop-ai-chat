"""
PromptTestLab – Test prompts with models.

Inputs: Prompt, Prompt version, Model, Temperature, Max tokens, Text input.
Button: Run Prompt.
Displays model output in a result panel.
"""

import asyncio
from typing import Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QTextEdit,
    QPushButton,
    QFormLayout,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


def _substitute_placeholders(content: str, user_input: str, context: str = "", topic: str = "") -> str:
    """Replace {{input}}, {{context}}, {{topic}} in prompt content."""
    result = content or ""
    result = result.replace("{{input}}", user_input or "")
    result = result.replace("{{context}}", context or "")
    result = result.replace("{{topic}}", topic or "")
    return result


class PromptTestLab(QFrame):
    """
    Test Lab for running prompts with models.

    - Prompt selection
    - Prompt version selection
    - Model selection
    - Temperature, Max tokens
    - Text input field
    - Run Prompt button
    - Result panel
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("promptTestLab")
        self._prompts: list = []
        self._versions: list = []
        self._models: list = []
        self._running = False
        self._setup_ui()
        self._connect_project_context()
        QTimer.singleShot(100, self._defer_load)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Prompt Test Lab")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1f2937;")
        layout.addWidget(title)

        # Inputs
        form = QFrame()
        form.setObjectName("testLabForm")
        form_layout = QFormLayout(form)
        form_layout.setSpacing(12)

        self._prompt_combo = QComboBox()
        self._prompt_combo.setMinimumWidth(280)
        self._prompt_combo.setPlaceholderText("Prompt auswählen…")
        self._prompt_combo.currentIndexChanged.connect(self._on_prompt_changed)
        form_layout.addRow("Prompt:", self._prompt_combo)

        self._version_combo = QComboBox()
        self._version_combo.setMinimumWidth(200)
        self._version_combo.setPlaceholderText("Version…")
        form_layout.addRow("Version:", self._version_combo)

        self._model_combo = QComboBox()
        self._model_combo.setMinimumWidth(200)
        self._model_combo.setPlaceholderText("Modell laden…")
        form_layout.addRow("Modell:", self._model_combo)

        temp_row = QHBoxLayout()
        self._temp_spin = QDoubleSpinBox()
        self._temp_spin.setRange(0.0, 2.0)
        self._temp_spin.setSingleStep(0.1)
        self._temp_spin.setValue(0.7)
        self._temp_spin.setDecimals(1)
        temp_row.addWidget(self._temp_spin)
        form_layout.addRow("Temperatur:", temp_row)

        tokens_row = QHBoxLayout()
        self._tokens_spin = QSpinBox()
        self._tokens_spin.setRange(1, 32768)
        self._tokens_spin.setValue(4096)
        tokens_row.addWidget(self._tokens_spin)
        form_layout.addRow("Max Tokens:", tokens_row)

        form.setStyleSheet("""
            #testLabForm {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        layout.addWidget(form)

        # Text input
        layout.addWidget(QLabel("Eingabe (ersetzt {{input}}):"))
        self._input_text = QTextEdit()
        self._input_text.setPlaceholderText("Text eingeben… ({{input}}, {{context}}, {{topic}} werden ersetzt)")
        self._input_text.setMaximumHeight(100)
        self._input_text.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self._input_text)

        # Run button
        self._run_btn = QPushButton("Run Prompt")
        self._run_btn.setObjectName("runPromptButton")
        self._run_btn.setStyleSheet("""
            #runPromptButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }
            #runPromptButton:hover { background: #1d4ed8; }
            #runPromptButton:disabled {
                background: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self._run_btn.clicked.connect(self._on_run)
        layout.addWidget(self._run_btn)

        # Result panel
        layout.addWidget(QLabel("Ergebnis:"))
        self._result_text = QTextEdit()
        self._result_text.setReadOnly(True)
        self._result_text.setMinimumHeight(200)
        self._result_text.setPlaceholderText("Ausgabe erscheint hier nach Run…")
        self._result_text.setFont(QFont("Monospace", 10))
        self._result_text.setStyleSheet("""
            QTextEdit {
                padding: 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: #f8fafc;
            }
        """)
        layout.addWidget(self._result_text, 1)

        self.setStyleSheet("""
            #promptTestLab {
                background: #ffffff;
            }
        """)

    def _connect_project_context(self) -> None:
        try:
            from app.gui.events.project_events import subscribe_project_events
            subscribe_project_events(self._on_project_context_changed)
        except Exception:
            pass

    def _on_project_context_changed(self, payload: dict) -> None:
        self._load_prompts()

    def _defer_load(self) -> None:
        """Defer load until event loop is ready."""
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self._load_all())
        except RuntimeError:
            QTimer.singleShot(100, self._defer_load)

    async def _load_all(self) -> None:
        """Load prompts and models."""
        await self._load_prompts_async()
        await self._load_models_async()

    def _load_prompts(self) -> None:
        """Synchronous entry for project change."""
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self._load_prompts_async())
        except RuntimeError:
            pass

    async def _load_prompts_async(self) -> None:
        """Load prompts for active project."""
        self._prompt_combo.blockSignals(True)
        self._prompt_combo.clear()
        self._prompts = []
        try:
            from app.prompts.prompt_service import get_prompt_service
            from app.core.context.project_context_manager import get_project_context_manager
            svc = get_prompt_service()
            mgr = get_project_context_manager()
            project_id = mgr.get_active_project_id()
            if project_id:
                self._prompts = svc.list_project_prompts(project_id, "") + svc.list_global_prompts("")
            else:
                self._prompts = svc.list_global_prompts("")
            for p in self._prompts:
                title = getattr(p, "title", "") or "Unbenannt"
                self._prompt_combo.addItem(title, p)
        except Exception:
            pass
        self._prompt_combo.blockSignals(False)
        self._on_prompt_changed()

    async def _load_models_async(self) -> None:
        """Load available models."""
        try:
            from app.services.model_service import get_model_service
            result = await get_model_service().get_models()
            self._models = result.data if result.success else []
            self._model_combo.clear()
            for m in self._models:
                self._model_combo.addItem(m)
            if self._models:
                default = get_model_service().get_default_model()
                idx = self._model_combo.findText(default)
                if idx >= 0:
                    self._model_combo.setCurrentIndex(idx)
        except Exception:
            self._model_combo.clear()
            self._model_combo.addItem("(Ollama nicht erreichbar)")

    def _on_prompt_changed(self) -> None:
        """Load versions when prompt changes."""
        self._version_combo.clear()
        self._versions = []
        idx = self._prompt_combo.currentIndex()
        if idx < 0:
            return
        prompt = self._prompt_combo.itemData(idx)
        if not prompt:
            return
        pid = getattr(prompt, "id", None)
        if pid is None:
            return
        try:
            from app.prompts.prompt_service import get_prompt_service
            self._versions = get_prompt_service().list_versions(pid)
            for v in self._versions:
                ver_num = v.get("version", 0)
                created = v.get("created_at")
                date_str = "—"
                if created:
                    try:
                        if hasattr(created, "strftime"):
                            date_str = created.strftime("%d.%m.%Y")
                        else:
                            date_str = str(created)[:10]
                    except Exception:
                        pass
                self._version_combo.addItem(f"v{ver_num} ({date_str})", v)
            if self._versions:
                self._version_combo.setCurrentIndex(0)
        except Exception:
            pass

    def _get_prompt_content(self) -> tuple[str, str]:
        """Get (title, content) for selected prompt/version."""
        idx = self._prompt_combo.currentIndex()
        if idx < 0:
            return ("", "")
        prompt = self._prompt_combo.itemData(idx)
        if not prompt:
            return ("", "")
        # Prefer selected version
        v_idx = self._version_combo.currentIndex()
        if v_idx >= 0 and self._versions:
            v = self._versions[v_idx]
            return (v.get("title", ""), v.get("content", ""))
        # Fallback to current prompt
        return (getattr(prompt, "title", "") or "", getattr(prompt, "content", "") or "")

    def _on_run(self) -> None:
        if self._running:
            return
        model = self._model_combo.currentText()
        if not model or model.startswith("("):
            self._result_text.setPlainText("Bitte ein Modell auswählen.")
            return
        title, content = self._get_prompt_content()
        if not content.strip():
            self._result_text.setPlainText("Bitte einen Prompt mit Inhalt auswählen.")
            return
        asyncio.create_task(self._run_prompt(model, title, content))

    async def _run_prompt(self, model: str, title: str, content: str) -> None:
        """Execute prompt and stream result."""
        self._running = True
        self._run_btn.setEnabled(False)
        self._result_text.clear()
        self._result_text.setPlainText("Wird ausgeführt…")

        user_input = self._input_text.toPlainText().strip()
        prompt_content = _substitute_placeholders(content, user_input)

        messages = [
            {"role": "system", "content": prompt_content},
            {"role": "user", "content": user_input or "(keine Eingabe)"},
        ]

        temperature = self._temp_spin.value()
        max_tokens = self._tokens_spin.value()

        full_content = ""
        last_error = None
        try:
            from app.services.chat_service import get_chat_service
            chat_svc = get_chat_service()
            async for chunk in chat_svc.chat(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            ):
                last_error = chunk.get("error")
                if last_error:
                    full_content = f"Fehler: {last_error}"
                    self._result_text.setPlainText(full_content)
                    break
                msg = chunk.get("message") or {}
                part = msg.get("content") or ""
                if part:
                    full_content += part
                    self._result_text.setPlainText(full_content)
                    scrollbar = self._result_text.verticalScrollBar()
                    if scrollbar:
                        scrollbar.setValue(scrollbar.maximum())
            if not full_content and not last_error:
                self._result_text.setPlainText("(Keine Ausgabe)")
        except Exception as e:
            self._result_text.setPlainText(f"Fehler: {e!s}")
        finally:
            self._running = False
            self._run_btn.setEnabled(True)
