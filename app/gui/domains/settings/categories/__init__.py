"""Settings category components – each category as separate extendable component."""

from app.gui.domains.settings.categories.application_category import ApplicationCategory
from app.gui.domains.settings.categories.appearance_category import AppearanceCategory
from app.gui.domains.settings.categories.ai_models_category import AIModelsCategory
from app.gui.domains.settings.categories.data_category import DataCategory
from app.gui.domains.settings.categories.privacy_category import PrivacyCategory
from app.gui.domains.settings.categories.advanced_category import AdvancedCategory
from app.gui.domains.settings.categories.project_category import ProjectCategory
from app.gui.domains.settings.categories.workspace_category import WorkspaceCategory

__all__ = [
    "ApplicationCategory",
    "AppearanceCategory",
    "AIModelsCategory",
    "DataCategory",
    "PrivacyCategory",
    "AdvancedCategory",
    "ProjectCategory",
    "WorkspaceCategory",
]
