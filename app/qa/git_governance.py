"""
Soft-Gates: welche Governance-Aussagen zu welchem Git-Zustand passen.

Keine Server-Hooks — reine Klassifikation für Berichte und Tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

from app.qa.git_context import GitContext

# Aussagen, die für Abnahme/Freigabe einen nachweisbaren Commit-Kontext brauchen
# (siehe docs/architecture/GIT_QA_GOVERNANCE.md).
STRONG_GOVERNANCE_CLAIMS: Final[frozenset[str]] = frozenset({
    "accepted",
    "architecture_approved",
    "release_candidate",
    "release_ready",
    "stable",
    "reproducible",
})


class FormalClaimTier(Enum):
    """
    Maximale Stufe formal dokumentierbarer Qualitätsaussagen.

    INFORMAL — explorativ, lokal, muss nicht im Report festgehalten werden.
    INFORMATIVE — dokumentierter Lauf ohne Abnahme/Freigabe.
    SIGN_OFF_ELIGIBLE — sauberer HEAD, Repo bekannt, geeignet für starke Claims (Soft-Gate: trotzdem Review).
    """

    INFORMAL = "informal"
    INFORMATIVE = "informative"
    SIGN_OFF_ELIGIBLE = "sign_off_eligible"


@dataclass(frozen=True, slots=True)
class SoftGateResult:
    """Ergebnis der Soft-Gate-Auswertung (kein harter Programmabbruch)."""

    max_formal_tier: FormalClaimTier
    strong_claims_allowed: bool
    warnings: tuple[str, ...]
    rationale: tuple[str, ...]


def evaluate_soft_gates(ctx: GitContext) -> SoftGateResult:
    """
    Bewertet den Git-Kontext für formale QA-/Release-Texte.

    - Kein Repo / kein Git: nur INFORMATIVE Berichte, keine starken Claims.
    - Dirty oder unklarer Status: starke Claims nicht zulässig (Soft-Block).
    - Sauberer Tree + bekannter Commit: SIGN_OFF_ELIGIBLE.
    """
    warnings: list[str] = []
    rationale: list[str] = []

    if not ctx.repository_present:
        warnings.append("Kein Git-Repository erkannt — Berichte nur als INFORMATIVE klassifizieren.")
        rationale.append("repository_present=false")
        return SoftGateResult(
            max_formal_tier=FormalClaimTier.INFORMATIVE,
            strong_claims_allowed=False,
            warnings=tuple(warnings),
            rationale=tuple(rationale),
        )

    if not ctx.has_resolved_commit:
        warnings.append("Kein auflösbarer HEAD-Commit — keine Abnahme-/Release-Claims mit Commit-Bezug.")
        rationale.append("head_commit missing (z. B. leeres Repo)")
        return SoftGateResult(
            max_formal_tier=FormalClaimTier.INFORMATIVE,
            strong_claims_allowed=False,
            warnings=tuple(warnings),
            rationale=tuple(rationale),
        )

    if ctx.error_reason:
        warnings.append(f"Git-Status eingeschränkt: {ctx.error_reason}")
        rationale.append("partial git error")

    if ctx.is_dirty:
        warnings.append(
            "Dirty Working Tree — Lauf ist nicht sauber reproduzierbar; "
            "starke Claims (accepted, release_ready, …) sind unzulässig."
        )
        rationale.append("is_dirty=true")
        return SoftGateResult(
            max_formal_tier=FormalClaimTier.INFORMATIVE,
            strong_claims_allowed=False,
            warnings=tuple(warnings),
            rationale=tuple(rationale),
        )

    if ctx.detached_head:
        warnings.append(
            "Detached HEAD — Commit ist bekannt, Branch nicht; für Freigaben Branch/Tag im Report nennen."
        )
        rationale.append("detached_head=true")

    rationale.append("clean tree + resolved commit")
    return SoftGateResult(
        max_formal_tier=FormalClaimTier.SIGN_OFF_ELIGIBLE,
        strong_claims_allowed=True,
        warnings=tuple(warnings),
        rationale=tuple(rationale),
    )


def strong_governance_claim_allowed(claim: str, ctx: GitContext) -> bool:
    """Ob eine einzelne starke Claim-Zeichenkette (siehe STRONG_GOVERNANCE_CLAIMS) erlaubt ist."""
    normalized = claim.strip().lower().replace(" ", "_").replace("-", "_")
    if normalized not in STRONG_GOVERNANCE_CLAIMS:
        return True
    return evaluate_soft_gates(ctx).strong_claims_allowed


def describe_allowed_claims_text(gate: SoftGateResult) -> str:
    """Kurztext für Report-Fußzeilen."""
    if gate.strong_claims_allowed:
        return (
            "Formal: SIGN_OFF_ELIGIBLE — starke Aussagen (accepted, release_ready, …) dürfen "
            "mit Commit-Referenz im Dokument genutzt werden (weiterhin menschliches Review)."
        )
    return (
        "Formal: INFORMATIVE — dokumentierbar ohne Abnahme; starke Aussagen erst nach sauberem "
        "Commit-Zustand oder mit explizitem „explorativ / vorläufig“-Kennzeichen."
    )
