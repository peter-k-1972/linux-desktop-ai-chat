"""
Central path definitions for docs/qa structure.

All QA scripts should use these paths instead of hardcoding.
"""
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_QA = _PROJECT_ROOT / "docs" / "qa"

# Artifacts
ARTIFACTS = DOCS_QA / "artifacts"
ARTIFACTS_DASHBOARDS = ARTIFACTS / "dashboards"
ARTIFACTS_JSON = ARTIFACTS / "json"
ARTIFACTS_CSV = ARTIFACTS / "csv"

# Governance
GOVERNANCE = DOCS_QA / "governance"
GOVERNANCE_SCHEMAS = GOVERNANCE / "schemas"
GOVERNANCE_INCIDENT_SCHEMAS = GOVERNANCE / "incident_schemas"

# Architecture (graphs written here)
ARCHITECTURE_GRAPHS = DOCS_QA / "architecture" / "graphs"

# Other
INCIDENTS = DOCS_QA / "incidents"
FEEDBACK_LOOP = DOCS_QA / "feedback_loop"
CONFIG = DOCS_QA / "config"
PLANS = DOCS_QA / "plans"
