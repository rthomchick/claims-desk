"""
Seed the Claims Desk registry with 12 Kalder product claims spanning all
four claim types. Product names/taglines/competitors are copied as plain
reference strings from kalder_data_model.py (buying-group-personalization-
advisor) — no import of that module; Kalder is read-only world-building
per ADR-016.

Claims #9 and #11 are deliberately unsubstantiated (missing evidence_url)
for Week 17 adversary testing. After seeding, classify_claim_risk is run
against all 12 claims and a summary table is printed.
"""

from __future__ import annotations

from server.tools.append_claim import append_claim
from server.tools.classify_claim_risk import classify_claim_risk
from server.db.client import fetchone_dict

SEED_CLAIMS = [
    dict(
        product_key="kalder_resolve",
        claim_type="performance",
        claim_text="AI autonomous triage reduces incident resolution time by 40%",
        evidence_url="https://kalder.example.com/reports/resolve-triage-benchmark-2026",
        evidence_date="2026-03-15",
        sample_size=214,
        baseline="pre-deployment incident resolution times across 214 enterprise customers",
    ),
    dict(
        product_key="kalder_observe",
        claim_type="performance",
        claim_text="Predictive outage prevention cuts unplanned downtime by 60%",
        evidence_url="https://kalder.example.com/reports/observe-downtime-study-2026",
        evidence_date="2026-02-10",
        sample_size=180,
        baseline="unplanned downtime hours pre- vs. post-deployment, 180 customer environments",
    ),
    dict(
        product_key="kalder_agents",
        claim_type="performance",
        claim_text="Teams deploy production agents in under 10 minutes",
        evidence_url="https://kalder.example.com/reports/agents-time-to-deploy-2026",
        evidence_date="2026-04-01",
        sample_size=95,
        baseline="median time-to-first-production-deployment across 95 onboarding sessions",
    ),
    dict(
        product_key="kalder_resolve",
        claim_type="comparative",
        claim_text="Faster time-to-resolution than ServiceNow ITSM Pro",
        evidence_url="https://kalder.example.com/reports/resolve-vs-servicenow-2026",
        evidence_date="2026-01-20",
        sample_size=60,
        baseline="ServiceNow ITSM Pro",
    ),
    dict(
        product_key="kalder_defend",
        claim_type="comparative",
        claim_text="More automated containment actions than Splunk SOAR",
        evidence_url="https://kalder.example.com/reports/defend-vs-splunk-soar-2026",
        evidence_date="2026-03-05",
        sample_size=40,
        baseline="Splunk SOAR",
    ),
    dict(
        product_key="kalder_predict",
        claim_type="comparative",
        claim_text="Lower cloud spend forecasting error than AWS Cost Explorer",
        evidence_url="https://kalder.example.com/reports/predict-vs-cost-explorer-2026",
        evidence_date="2026-02-28",
        sample_size=75,
        baseline="AWS Cost Explorer",
    ),
    dict(
        product_key="kalder_govern",
        claim_type="compliance",
        claim_text="SOC 2 Type II certified AI governance platform",
        evidence_url="https://kalder.example.com/certs/govern-soc2-type2-2026.pdf",
        evidence_date="2026-06-01",
        expiry_date="2027-06-10",
    ),
    dict(
        product_key="kalder_asset",
        claim_type="compliance",
        claim_text="ISO 27001 certified compliance reporting",
        evidence_url="https://kalder.example.com/certs/asset-iso27001-2026.pdf",
        evidence_date="2026-05-15",
        expiry_date="2027-06-10",
    ),
    dict(
        product_key="kalder_vendor",
        claim_type="compliance",
        claim_text="FedRAMP Moderate authorized for federal vendor risk workflows",
        # Deliberately weak: no evidence_url, no expiry_date. Fabricated
        # claim not present anywhere in the Kalder data model's actual
        # platform capabilities. Left unsubstantiated on purpose.
    ),
    dict(
        product_key="kalder_observe",
        claim_type="superlative",
        claim_text="#1 rated AIOps platform on G2",
        evidence_url="https://kalder.example.com/awards/g2-aiops-2026",
        evidence_date="2026-06-20",
    ),
    dict(
        product_key="kalder_insight",
        claim_type="superlative",
        claim_text="The most-deployed cross-product analytics platform in IT service management",
        # Deliberately weak: no evidence_url, no named source.
        evidence_date="2026-05-01",
    ),
    dict(
        product_key="kalder_agents",
        claim_type="superlative",
        claim_text="Recognized as a Leader in the 2026 agent platform category",
        evidence_url="https://kalder.example.com/awards/agent-platform-leader-2026",
        evidence_date="2026-04-15",
    ),
]


def seed() -> list[str]:
    claim_ids = []
    for entry in SEED_CLAIMS:
        result = append_claim(**entry)
        claim_ids.append(result["claim_id"])
        print(f"seeded {entry['product_key']} / {entry['claim_type']}: {result['claim_id']}")
    return claim_ids


def classify_all(claim_ids: list[str]) -> None:
    print("\nclassify_claim_risk summary:")
    print(f"{'claim_id':<38} {'product_key':<16} {'claim_type':<12} {'risk_class':<10}")
    print("-" * 78)
    for claim_id in claim_ids:
        classify_claim_risk(claim_id)
        row = fetchone_dict(
            "select claim_id, product_key, claim_type, risk_class from claims where claim_id = %s",
            (claim_id,),
        )
        print(
            f"{str(row['claim_id']):<38} {row['product_key']:<16} "
            f"{row['claim_type']:<12} {row['risk_class']:<10}"
        )


if __name__ == "__main__":
    ids = seed()
    classify_all(ids)
