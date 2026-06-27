from typing import List

from pydantic import BaseModel, Field


class DrugAlternative(BaseModel):
    """
    A single therapeutic alternative suggestion.
    """

    name: str = Field(
        description="Generic name of the alternative medicine."
    )

    drug_class: str | None = Field(
        default=None,
        description="Pharmacological / therapeutic class of the alternative."
    )

    similarity_notes: str = Field(
        description=(
            "Brief clinical note on why this is a reasonable "
            "substitute (e.g. same class, same indication, "
            "different class but overlapping indication)."
        )
    )

    caution: str | None = Field(
        default=None,
        description=(
            "Important caveat a clinician should know before "
            "substituting (e.g. dosing differences, contraindications, "
            "narrower therapeutic index). Null if none."
        )
    )


class AlternativesReport(BaseModel):
    """
    Final output of the Drug Alternatives Agent.

    This report is generated when a medicine is facing a
    potential shortage and therapeutic alternatives need to
    be suggested for supply-chain planning purposes.

    It is intended to be displayed directly on the dashboard.
    """

    # =====================================================
    # Query Information
    # =====================================================

    queried_medicine: str = Field(
        description="The medicine the user searched for or that was flagged at-risk."
    )

    recognized: bool = Field(
        description=(
            "Whether the queried medicine was recognized as a "
            "real, known pharmaceutical product/generic."
        )
    )

    therapeutic_class: str | None = Field(
        default=None,
        description="Therapeutic class of the queried medicine, if recognized."
    )

    # =====================================================
    # Alternatives
    # =====================================================

    alternatives: List[DrugAlternative] = Field(
        default_factory=list,
        description="List of suggested therapeutic alternatives."
    )

    # =====================================================
    # Context (optional, populated when linked to a RiskReport)
    # =====================================================

    shortage_context: str | None = Field(
        default=None,
        description=(
            "If this medicine is currently flagged at-risk by the "
            "Risk Agent, a brief note on why."
        )
    )

    # =====================================================
    # Supporting Evidence
    # =====================================================

    web_sources: List[str] = Field(
        default_factory=list,
        description=(
            "URLs of web sources used to support the suggested "
            "alternatives. Empty if no reliable evidence was found."
        )
    )

    # =====================================================
    # Disclaimer / Confidence
    # =====================================================

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1."
    )

    disclaimer: str = Field(
        default=(
            "These suggestions are for supply-chain planning only "
            "and must be reviewed by a licensed clinician before "
            "any therapeutic substitution."
        ),
        description="Standard safety disclaimer shown with the result."
    )