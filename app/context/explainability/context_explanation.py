"""
Context explainability – pure dataclasses for traceability.

No logic, no UI imports.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ContextSourceEntry:
    """Eintrag für eine Kontext-Quelle."""

    source_type: str
    identifier: str = ""
    included: bool = True
    chars_before: Optional[int] = None
    chars_after: Optional[int] = None
    chars: Optional[int] = None
    lines: Optional[int] = None
    # Per-source budget accounting (instrumentation only)
    budget_allocated: Optional[int] = None  # max chars for this source
    budget_used: Optional[int] = None  # chars in final fragment
    budget_dropped: Optional[int] = None  # chars dropped (truncation or skip)
    selection_order: Optional[int] = None  # 1=project, 2=chat, 3=topic; required for resolver-built sources
    reason: str = ""  # "budget_exhausted" | "truncated_to_budget" | ""


@dataclass(frozen=True)
class ContextDecisionEntry:
    """Eintrag für eine Kontext-Entscheidung."""

    decision_type: str
    reason: str = ""
    outcome: str = ""


@dataclass(frozen=True)
class ContextCompressionEntry:
    """Eintrag für einen Kontext-Komprimierungsschritt."""

    operation: str
    original_chars: Optional[int] = None
    final_chars: Optional[int] = None
    before_tokens: Optional[int] = None
    after_tokens: Optional[int] = None
    dropped_tokens: Optional[int] = None
    reason: str = ""


@dataclass(frozen=True)
class ContextWarningEntry:
    """
    Eintrag für eine Fail-Safe-Warnung.

    Attributes:
        warning_type: header_only_fragment_removed | marker_only_fragment_removed |
            empty_injection_prevented | failsafe | budget_overflow_prevented | ...
        message: Optional human-readable detail (e.g. mode=off, fragment_empty)
        source_type: Optional – project | chat | topic | context
        source_id: Optional – identifier for the source
        effect: removed_fragment | skipped_injection (when failsafe changed payload)
        dropped_tokens: Optional – tokens dropped by this failsafe action
    """

    warning_type: str
    message: str = ""
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    effect: Optional[str] = None  # removed_fragment | skipped_injection
    dropped_tokens: Optional[int] = None


@dataclass(frozen=True)
class ContextSettingCandidate:
    """
    Ein Kandidat für eine Kontext-Einstellung in der Prioritätskette.

    Attributes:
        priority_index: 0 = höchste Priorität (profile_enabled), 5 = niedrigste (individual_settings)
        source: profile_enabled | explicit_context_policy | chat_default_context_policy |
                project_default_context_policy | request_context_hint | individual_settings
        value: Der Wert, den dieser Kandidat liefern würde (mode, detail, bool, etc.)
        applied: True wenn dieser Kandidat gewonnen hat
        skipped_reason: Optional – warum übersprungen (z.B. "higher_priority_won", "source_not_present", "invalid")
    """

    priority_index: int
    source: str
    value: str | bool | None
    applied: bool
    skipped_reason: Optional[str] = None


@dataclass(frozen=True)
class ContextResolvedSettingEntry:
    """
    Aufgelöste Einstellung mit vollständiger Prioritätskette.

    Zeigt genau, welcher Override-Layer für den effektiven Wert gewonnen hat.

    Attributes:
        setting_name: mode | detail_level | policy | project_enabled | chat_enabled | topic_enabled
        final_value: Der effektive Wert
        winning_source: profile_enabled | explicit_context_policy | chat_default_context_policy |
                        project_default_context_policy | request_context_hint | individual_settings
        candidates: Geordnete Liste aller evaluierten Kandidaten (Prioritätsreihenfolge)
        fallback_used: True wenn individual_settings gewonnen hat (alle höheren Kandidaten fehlten)
    """

    setting_name: str
    final_value: str | bool | None
    winning_source: str
    candidates: List[ContextSettingCandidate]
    fallback_used: bool


@dataclass(frozen=True)
class ContextIgnoredInputEntry:
    """
    Eintrag für ignorierten oder ungültigen Kontext-Input.

    Entwickler und QA sehen, wann Request-/Profil-/Projekt-/Chat-Einstellungen ignoriert wurden.

    Attributes:
        input_name: Name des Inputs (z.B. mode, detail_level, policy, request_context_hint,
                    project, chat, topic, chat_context_profile)
        input_source: Herkunft (request | settings | profile | chat | project)
        raw_value: Der ursprüngliche/rohe Wert
        reason: invalid_value | unsupported_policy | disabled_by_profile | field_disabled | empty_source | source_not_found
        resolution_effect: ignored | fallback_used | field_disabled
    """

    input_name: str
    input_source: str
    raw_value: str | bool | None
    reason: str
    resolution_effect: str


@dataclass(frozen=True)
class ContextDroppedEntry:
    """Eintrag für abgeworfenen Kontext (metadata only, no content preview)."""

    source_type: str
    reason: str  # policy_exclusion | field_disabled | profile_restriction | compression | token_budget_exhaustion | failsafe_cleanup
    dropped_tokens: Optional[int] = None
    source_id: Optional[str] = None


@dataclass(frozen=True)
class ContextExplanation:
    """Aggregierte Erklärung der Kontext-Auflösung."""

    sources: List[ContextSourceEntry] = field(default_factory=list)
    decisions: List[ContextDecisionEntry] = field(default_factory=list)
    resolved_settings: List[ContextResolvedSettingEntry] = field(default_factory=list)
    compressions: List[ContextCompressionEntry] = field(default_factory=list)
    warnings: List[ContextWarningEntry] = field(default_factory=list)
    ignored_inputs: List[ContextIgnoredInputEntry] = field(default_factory=list)

    # Token budget accounting (instrumentation only, deterministic)
    configured_budget_total: Optional[int] = None  # tokens from limits (chars/4)
    effective_budget_total: Optional[int] = None  # after any capping
    total_tokens_after: Optional[int] = None  # sum(source.budget_used // 4) for included sources
    reserved_budget_system: Optional[int] = None  # tokens for labels/overhead
    reserved_budget_user: Optional[int] = None  # reserved for user (0 if unused)
    available_budget_for_context: Optional[int] = None  # effective - reserved
    budget_strategy: Optional[str] = None  # e.g. "per_field_and_lines"
    budget_source: Optional[str] = None  # same as limits_source

    # Dropped context reporting (metadata only, no content preview)
    dropped_total_tokens: Optional[int] = None
    dropped_by_source: List[ContextDroppedEntry] = field(default_factory=list)
    dropped_reasons: List[str] = field(default_factory=list)

    # Failsafe explainability (trace only)
    warning_count: int = 0
    failsafe_triggered: bool = False

    # Empty-result markers (explainability for edge cases; no behavioral change)
    empty_result: bool = False
    empty_result_reason: Optional[str] = None  # no_sources | excluded_by_policy | disabled_mode | failsafe_cleanup | budget_exhausted
