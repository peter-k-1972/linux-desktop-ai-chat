"""
QML-Kontextobjekt für Prompt Studio (``promptStudio``).

Properties: prompts, selectedPrompt, collections, tags
Slots: selectPrompt, createPrompt, savePrompt
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Property, QObject, QStringListModel, Signal, Slot

from python_bridge.prompts.prompt_models import (
    PromptShelfListModel,
    VariantListModel,
    format_variables_line,
)
from python_bridge.prompts.prompt_presenter_facade import PromptPresenterFacade

if TYPE_CHECKING:
    from app.prompts.prompt_models import Prompt as PromptEntity

logger = logging.getLogger(__name__)


class _PromptSelection(QObject):
    """Aktuell fokussierter Prompt — Felder für Lesepult-Bindings."""

    promptIdChanged = Signal()
    titleChanged = Signal()
    descriptionChanged = Signal()
    contentChanged = Signal()
    variablesChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._prompt_id: int = -1
        self._title: str = ""
        self._description: str = ""
        self._content: str = ""
        self._variables: str = ""

    def _get_id(self) -> int:
        return self._prompt_id

    def _set_id(self, value: int) -> None:
        if self._prompt_id != value:
            self._prompt_id = value
            self.promptIdChanged.emit()

    promptId = Property(int, _get_id, _set_id, notify=promptIdChanged)

    def _get_title(self) -> str:
        return self._title

    def _set_title(self, value: str) -> None:
        v = value or ""
        if self._title != v:
            self._title = v
            self.titleChanged.emit()

    title = Property(str, _get_title, _set_title, notify=titleChanged)

    def _get_description(self) -> str:
        return self._description

    def _set_description(self, value: str) -> None:
        v = value or ""
        if self._description != v:
            self._description = v
            self.descriptionChanged.emit()

    description = Property(str, _get_description, _set_description, notify=descriptionChanged)

    def _get_content(self) -> str:
        return self._content

    def _set_content(self, value: str) -> None:
        v = value or ""
        if self._content != v:
            self._content = v
            self._sync_variables()
            self.contentChanged.emit()

    content = Property(str, _get_content, _set_content, notify=contentChanged)

    def _get_variables(self) -> str:
        return self._variables

    variables = Property(str, _get_variables, notify=variablesChanged)

    def _sync_variables(self) -> None:
        line = format_variables_line(self._content)
        if line != self._variables:
            self._variables = line
            self.variablesChanged.emit()

    def backend_id(self) -> int | None:
        return self._prompt_id if self._prompt_id >= 0 else None

    def load_from(self, entity: PromptEntity | None) -> None:
        if entity is None or entity.id is None:
            self._prompt_id = -1
            self._title = ""
            self._description = ""
            self._content = ""
            self._variables = ""
            self.promptIdChanged.emit()
            self.titleChanged.emit()
            self.descriptionChanged.emit()
            self.contentChanged.emit()
            self.variablesChanged.emit()
            return
        self._prompt_id = int(entity.id)
        self._title = entity.title or ""
        self._description = entity.description or ""
        self._content = entity.content or ""
        self._variables = format_variables_line(self._content)
        self.promptIdChanged.emit()
        self.titleChanged.emit()
        self.descriptionChanged.emit()
        self.contentChanged.emit()
        self.variablesChanged.emit()


class PromptViewModel(QObject):
    promptsChanged = Signal()
    selectedPromptChanged = Signal()
    collectionsChanged = Signal()
    tagsChanged = Signal()
    variantsChanged = Signal()
    searchTextChanged = Signal()
    activeCollectionChanged = Signal()
    activeTagChanged = Signal()
    variantDrawerOpenChanged = Signal()

    def __init__(
        self,
        facade: PromptPresenterFacade | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._facade = facade or PromptPresenterFacade()
        self._shelf = PromptShelfListModel(self)
        self._variants = VariantListModel(self)
        self._collections = QStringListModel(self)
        self._tags = QStringListModel(self)
        self._selected = _PromptSelection(self)
        self._search_text: str = ""
        self._active_collection: str = ""
        self._active_tag: str = ""
        self._all_loaded: list = []
        self._variant_drawer_open: bool = False
        self.reload()

    def _get_prompts(self) -> PromptShelfListModel:
        return self._shelf

    prompts = Property(QObject, _get_prompts, notify=promptsChanged)

    def _get_selected_prompt(self) -> _PromptSelection:
        return self._selected

    selectedPrompt = Property(QObject, _get_selected_prompt, notify=selectedPromptChanged)

    def _get_collections(self) -> QStringListModel:
        return self._collections

    collections = Property(QObject, _get_collections, notify=collectionsChanged)

    def _get_tags(self) -> QStringListModel:
        return self._tags

    tags = Property(QObject, _get_tags, notify=tagsChanged)

    def _get_variants(self) -> VariantListModel:
        return self._variants

    variants = Property(QObject, _get_variants, notify=variantsChanged)

    def _get_search(self) -> str:
        return self._search_text

    def _set_search(self, value: str) -> None:
        v = value or ""
        if self._search_text != v:
            self._search_text = v
            self.searchTextChanged.emit()
            self.reload()

    searchText = Property(str, _get_search, _set_search, notify=searchTextChanged)

    def _get_active_collection(self) -> str:
        return self._active_collection

    activeCollection = Property(str, _get_active_collection, notify=activeCollectionChanged)

    def _get_active_tag(self) -> str:
        return self._active_tag

    activeTag = Property(str, _get_active_tag, notify=activeTagChanged)

    def _get_drawer_open(self) -> bool:
        return self._variant_drawer_open

    def _set_drawer_open(self, value: bool) -> None:
        if self._variant_drawer_open != value:
            self._variant_drawer_open = value
            self.variantDrawerOpenChanged.emit()

    variantDrawerOpen = Property(bool, _get_drawer_open, _set_drawer_open, notify=variantDrawerOpenChanged)

    def _current_selected_id(self) -> int | None:
        return self._selected.backend_id()

    def reload(self) -> None:
        self._all_loaded = self._facade.list_prompts(self._search_text)
        cols = self._facade.unique_collections(self._all_loaded)
        self._collections.setStringList([""] + cols)
        tags = self._facade.unique_tags(self._all_loaded)
        self._tags.setStringList([""] + tags)
        self.collectionsChanged.emit()
        self.tagsChanged.emit()
        self._apply_shelf_rows()

    def _apply_shelf_rows(self) -> None:
        filtered = self._facade.filter_prompts(
            self._all_loaded,
            collection=self._active_collection,
            tag=self._active_tag,
        )
        sid = self._current_selected_id()
        rows: list[dict[str, object]] = []
        for p in filtered:
            pid = p.id
            if pid is None:
                continue
            tags_line = ", ".join((t or "").strip() for t in (p.tags or []) if (t or "").strip())
            rows.append(
                {
                    "promptId": int(pid),
                    "title": p.title or f"Prompt {pid}",
                    "category": (p.category or "").strip() or "—",
                    "tagsLine": tags_line,
                }
            )
        self._shelf.set_prompts(rows, sid)
        self.promptsChanged.emit()
        self._refresh_variants()

    def _refresh_variants(self) -> None:
        sid = self._current_selected_id()
        if sid is None:
            self._variants.set_versions([])
        else:
            self._variants.set_versions(self._facade.list_versions(sid))
        self.variantsChanged.emit()

    @Slot(int)
    def selectPrompt(self, prompt_id: int) -> None:  # noqa: N802
        if prompt_id < 0:
            self._selected.load_from(None)
            self._shelf.update_selection(None)
            self.selectedPromptChanged.emit()
            self._refresh_variants()
            return
        entity = self._facade.get(prompt_id)
        if entity is None:
            return
        self._selected.load_from(entity)
        self._shelf.update_selection(prompt_id)
        self.selectedPromptChanged.emit()
        self._refresh_variants()

    @Slot()
    def createPrompt(self) -> None:  # noqa: N802
        from app.prompts.prompt_models import Prompt

        draft = Prompt.empty()
        draft.title = "Neuer Prompt"
        created = self._facade.create(draft)
        if created is None or created.id is None:
            logger.warning("createPrompt failed")
            return
        self.reload()
        self.selectPrompt(int(created.id))

    @Slot()
    def savePrompt(self) -> None:  # noqa: N802
        sid = self._selected.backend_id()
        if sid is None:
            return
        full = self._facade.get(sid)
        if full is None:
            return
        title = (self._selected.title or "").strip()
        if not title:
            logger.warning("savePrompt: title empty")
            return
        full.title = title
        full.description = self._selected.description or ""
        full.content = self._selected.content or ""
        if self._facade.update(full):
            self.reload()
            self.selectPrompt(int(full.id))

    @Slot(str)
    def setActiveCollection(self, name: str) -> None:
        v = (name or "").strip()
        if self._active_collection == v:
            return
        self._active_collection = v
        self.activeCollectionChanged.emit()
        self._apply_shelf_rows()

    @Slot(str)
    def setActiveTag(self, name: str) -> None:
        v = (name or "").strip()
        if self._active_tag == v:
            return
        self._active_tag = v
        self.activeTagChanged.emit()
        self._apply_shelf_rows()

    @Slot()
    def toggleVariantDrawer(self) -> None:
        self._set_drawer_open(not self._variant_drawer_open)

    @Slot(str, str)
    def applyVersionContent(self, _version: str, content: str) -> None:
        """Setzt den Prompt-Text aus einer gespeicherten Version (Lesepult)."""
        del _version
        self._selected.content = content or ""


def build_prompt_viewmodel() -> PromptViewModel:
    return PromptViewModel()
