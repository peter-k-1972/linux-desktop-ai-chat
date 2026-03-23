"""
Python-side layout rhythm for Workbench widgets.

QSS in ``assets/themes/base/workbench.qss`` is the visual source of truth; these
values keep margins consistent where layouts are built in code.
"""

from __future__ import annotations

# Multiples of 4px, aligned with ThemeTokens.spacing_*
INSPECTOR_INNER_MARGIN_PX: int = 12
EXPLORER_TREE_INDENT_PX: int = 20
