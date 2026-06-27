from typing import List, Optional

from models.alternatives_schema import AlternativesReport
from models.risk_schema import RiskReport

from services.alternatives_service import AlternativesService
from chains.alternatives_chain import find_alternatives


class AlternativesAgent:
    """
    Drug Alternatives Agent

    Responsibilities
    ----------------
    1. Receive a medicine name (manual search) OR RiskReports
       (auto-suggest for medicines already flagged at-risk).
    2. Retrieve supporting web evidence via AlternativesService
       (Tavily, dedicated key — see services/alternatives_service.py).
    3. Pass that evidence to the Alternatives Chain, which is
       constrained to synthesize ONLY from the supplied evidence.
    4. Return structured AlternativesReports.

    This mirrors ResearchAgent's collect-then-synthesize pattern:
    retrieval happens first, the LLM never reasons from memory alone.
    """

    def __init__(self):

        self.alternatives_service = AlternativesService()

    # ------------------------------------------------------
    # Manual single lookup
    # ------------------------------------------------------

    def lookup(
        self,
        medicine_name: str,
    ) -> AlternativesReport:
        """
        Look up alternatives for a single, user-provided
        medicine name. No shortage context attached.
        """

        medicine_name = medicine_name.strip()

        print(f"\nLooking up alternatives for: {medicine_name}")

        try:

            results = self.alternatives_service.search(medicine_name)
            evidence = self.alternatives_service.format_results(results)
            sources = [r["url"] for r in results if r.get("url")]

            print(f"✓ Retrieved {len(results)} web sources")

        except Exception as e:

            print(f"\nEvidence retrieval failed: {e}\n")
            evidence = "No reliable web evidence found for this medicine."
            sources = []

        return find_alternatives(
            medicine_name=medicine_name,
            evidence=evidence,
            web_sources=sources,
            shortage_context=None,
        )

    # ------------------------------------------------------
    # Batch lookup from Risk Agent output
    # ------------------------------------------------------

    def suggest_for_risk_reports(
        self,
        risk_reports: List[RiskReport],
        max_medicines: Optional[int] = 10,
    ) -> List[AlternativesReport]:
        """
        Auto-suggest alternatives for every distinct medicine
        flagged as affected in the supplied RiskReports.

        Medicines are de-duplicated (case-insensitive) and,
        when max_medicines is set, capped to limit Tavily/Groq
        calls on the dedicated Alternatives keys.
        """

        if not risk_reports:
            return []

        # --------------------------------------------------
        # Collect distinct medicines + their shortage context
        # --------------------------------------------------

        medicine_context: dict[str, tuple] = {}

        for report in risk_reports:

            context = (
                f"Flagged {report.overall_risk} risk "
                f"(score {report.risk_score}/100) due to: "
                f"{report.headline}. "
                f"Estimated shortage time: {report.estimated_shortage_time}."
            )

            for med in report.affected_medicines:

                key = med.strip().lower()

                if not key:
                    continue

                # Keep the highest-risk context if a medicine
                # appears in multiple reports.
                if key not in medicine_context:
                    medicine_context[key] = (med, context, report.risk_score)
                else:
                    _, _, existing_score = medicine_context[key]
                    if report.risk_score > existing_score:
                        medicine_context[key] = (med, context, report.risk_score)

        if not medicine_context:
            return []

        # --------------------------------------------------
        # Sort by risk score (highest first), cap if requested
        # --------------------------------------------------

        ordered = sorted(
            medicine_context.values(),
            key=lambda v: v[2],
            reverse=True,
        )

        if max_medicines is not None:
            ordered = ordered[:max_medicines]

        # --------------------------------------------------
        # Retrieve evidence + run the chain for each medicine
        # --------------------------------------------------

        reports: List[AlternativesReport] = []

        total = len(ordered)

        for index, (medicine_name, context, score) in enumerate(ordered, start=1):

            print("\n" + "=" * 100)
            print(f"[{index}/{total}] Finding Alternatives")
            print("=" * 100)
            print(f"Medicine : {medicine_name}")
            print(f"Context  : {context}")

            try:

                results = self.alternatives_service.search(medicine_name)
                evidence = self.alternatives_service.format_results(results)
                sources = [r["url"] for r in results if r.get("url")]

                print(f"✓ Retrieved {len(results)} web sources")

                report = find_alternatives(
                    medicine_name=medicine_name,
                    evidence=evidence,
                    web_sources=sources,
                    shortage_context=context,
                )

                reports.append(report)

                print("✓ Alternatives found")

            except Exception as e:

                print(
                    f"\nAlternatives Lookup Failed\n"
                    f"Medicine : {medicine_name}\n"
                    f"Reason   : {e}\n"
                )

        return reports


# ==========================================================
# Testing
# ==========================================================

if __name__ == "__main__":

    agent = AlternativesAgent()

    # ------------------------------------------------------
    # Manual lookup test
    # ------------------------------------------------------

    report = agent.lookup("Amoxicillin")

    print("\n")
    print("=" * 100)
    print("MANUAL LOOKUP RESULT")
    print("=" * 100)

    print(f"Queried Medicine  : {report.queried_medicine}")
    print(f"Recognized        : {report.recognized}")
    print(f"Therapeutic Class : {report.therapeutic_class}")

    for alt in report.alternatives:
        print(f"\n• {alt.name} ({alt.drug_class})")
        print(f"  {alt.similarity_notes}")
        if alt.caution:
            print(f"  ⚠ {alt.caution}")

    print("\nWeb Sources")
    for s in report.web_sources:
        print(f"- {s}")