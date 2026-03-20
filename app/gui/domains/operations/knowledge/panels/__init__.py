"""Knowledge Panels."""

from app.gui.domains.operations.knowledge.panels.knowledge_source_explorer_panel import (
    KnowledgeSourceExplorerPanel,
)
from app.gui.domains.operations.knowledge.panels.knowledge_overview_panel import (
    KnowledgeOverviewPanel,
)
from app.gui.domains.operations.knowledge.panels.retrieval_test_panel import (
    RetrievalTestPanel,
)
from app.gui.domains.operations.knowledge.panels.source_list_item import (
    SourceListItemWidget,
)
from app.gui.domains.operations.knowledge.panels.source_details_panel import (
    SourceDetailsPanel,
)
from app.gui.domains.operations.knowledge.panels.collection_panel import (
    CollectionPanel,
)
from app.gui.domains.operations.knowledge.panels.collection_dialog import (
    CreateCollectionDialog,
    RenameCollectionDialog,
    AssignSourcesDialog,
)
from app.gui.domains.operations.knowledge.panels.index_status_page import (
    IndexStatusPage,
)
from app.gui.domains.operations.knowledge.panels.chunk_viewer_panel import (
    ChunkViewerPanel,
)
from app.gui.domains.operations.knowledge.panels.knowledge_navigation_panel import (
    KnowledgeNavigationPanel,
    KNOWLEDGE_SECTIONS,
)

# Legacy names for compatibility
IndexOverviewPanel = KnowledgeOverviewPanel
RetrievalStatusPanel = RetrievalTestPanel
SourceListItem = SourceListItemWidget

__all__ = [
    "KnowledgeSourceExplorerPanel",
    "KnowledgeOverviewPanel",
    "RetrievalTestPanel",
    "SourceListItemWidget",
    "SourceListItem",
    "SourceDetailsPanel",
    "CollectionPanel",
    "CreateCollectionDialog",
    "RenameCollectionDialog",
    "AssignSourcesDialog",
    "IndexStatusPage",
    "ChunkViewerPanel",
    "KnowledgeNavigationPanel",
    "KNOWLEDGE_SECTIONS",
    "IndexOverviewPanel",
    "RetrievalStatusPanel",
]
