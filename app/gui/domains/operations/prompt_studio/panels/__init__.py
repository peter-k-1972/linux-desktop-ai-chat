"""Prompt Studio Panels."""

from app.gui.domains.operations.prompt_studio.panels.library_panel import PromptLibraryPanel
from app.gui.domains.operations.prompt_studio.panels.editor_panel import PromptEditorPanel as PromptEditorPanelFull  # Full editor with scope/category
from app.gui.domains.operations.prompt_studio.panels.preview_panel import PromptPreviewPanel
from app.gui.domains.operations.prompt_studio.panels.prompt_list_item import (
    PromptListItem,
    PromptListItemWidget,
)
from app.gui.domains.operations.prompt_studio.panels.prompt_navigation_panel import (
    PromptNavigationPanel,
    SECTION_PROMPTS,
    SECTION_TEMPLATES,
    SECTION_TEST_LAB,
)
from app.gui.domains.operations.prompt_studio.panels.prompt_list_panel import PromptListPanel
from app.gui.domains.operations.prompt_studio.panels.prompt_editor_panel import PromptEditorPanel
from app.gui.domains.operations.prompt_studio.panels.prompt_templates_panel import PromptTemplatesPanel
from app.gui.domains.operations.prompt_studio.panels.prompt_test_lab import PromptTestLab
from app.gui.domains.operations.prompt_studio.panels.prompt_version_panel import PromptVersionPanel

__all__ = [
    "PromptLibraryPanel",
    "PromptEditorPanel",
    "PromptEditorPanelFull",
    "PromptPreviewPanel",
    "PromptListItem",
    "PromptListItemWidget",
    "PromptNavigationPanel",
    "SECTION_PROMPTS",
    "SECTION_TEMPLATES",
    "SECTION_TEST_LAB",
    "PromptListPanel",
    "PromptTemplatesPanel",
    "PromptTestLab",
    "PromptVersionPanel",
]
