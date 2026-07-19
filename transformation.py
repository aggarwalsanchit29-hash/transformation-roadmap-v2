"""
transformation.py
-----------------
AI-powered roadmap generation for ERP, CRM, and Tech modules.
Uses Groq free tier.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

PROMPTS = {
    "erp": """You are a senior SAP/ERP transformation consultant with 20 years experience.

Generate a structured ERP/SAP transformation roadmap for **{company}**.

CONTEXT:
- Sector: {sector}
- Current Maturity: {maturity}
- Sector ERP Context: {module_context}

FORMAT WITH THESE EXACT ## HEADERS:

## Current State Assessment
[3-4 bullet points: typical ERP pain points and legacy challenges for a {sector} organisation at {maturity} maturity]

## Recommended ERP Strategy
[3-4 bullet points: SAP S/4HANA vs alternatives, deployment model (cloud/hybrid/on-premise), business case rationale]

## Phase 1: Foundation (Months 1-4)
[4-5 bullet points: discovery, blueprint, system landscape assessment, governance setup, quick wins]

## Phase 2: Core Implementation (Months 5-12)
[4-5 bullet points: core modules deployment, data migration, process redesign, change management]

## Phase 3: Optimise & Scale (Months 13-18)
[3-4 bullet points: advanced capabilities, AI/analytics integration, continuous improvement]

## Key Workstreams
[5-6 bullet points: Finance, Supply Chain, HR/Payroll, Procurement, Reporting, Integration]

## Critical Success Factors
[4 bullet points: executive sponsorship, data quality, change management, system integrator selection]

## Risks & Mitigations
[4 bullet points: each with risk and mitigation paired together]

## Indicative Investment
[3 bullet points: typical cost ranges for {sector}, ROI timeline, key cost drivers]

Be specific to {sector}. Use SAP/ERP terminology throughout.""",

    "crm": """You are a senior Salesforce/CRM transformation consultant.

Generate a structured CRM/Salesforce transformation roadmap for **{company}**.

CONTEXT:
- Sector: {sector}
- Current Maturity: {maturity}
- Sector CRM Context: {module_context}

FORMAT WITH THESE EXACT ## HEADERS:

## Current State Assessment
[3-4 bullet points: typical CRM challenges and customer data issues for {sector} at {maturity} maturity]

## Recommended Salesforce Architecture
[3-4 bullet points: which Salesforce clouds to implement (Sales/Service/Marketing/Industry), rationale, integration approach]

## Phase 1: Foundation (Months 1-3)
[4-5 bullet points: data model design, data migration, Sales Cloud core, user onboarding]

## Phase 2: Service & Automation (Months 4-9)
[4-5 bullet points: Service Cloud, process automation, Einstein Analytics, integrations]

## Phase 3: Marketing & Intelligence (Months 10-15)
[3-4 bullet points: Marketing Cloud, journey builder, AI-driven personalisation, advanced analytics]

## Key Capabilities Unlocked
[5-6 bullet points: what the business can do after implementation — specific to {sector}]

## Change Management & Adoption
[4 bullet points: user adoption strategy, training approach, governance model, KPIs for success]

## Risks & Mitigations
[4 bullet points: data quality, adoption, integration complexity, licensing costs]

## Indicative Investment
[3 bullet points: Salesforce licensing model, implementation costs, ongoing costs]

Be specific to {sector}. Use Salesforce terminology (orgs, objects, flows, Einstein, etc.).""",

    "tech": """You are a Chief Technology Officer and digital transformation expert.

Generate a structured Technology Enablement roadmap for **{company}**.

CONTEXT:
- Sector: {sector}
- Current Maturity: {maturity}
- Sector Tech Context: {module_context}

FORMAT WITH THESE EXACT ## HEADERS:

## Technology Landscape Assessment
[3-4 bullet points: typical legacy tech debt and modernisation needs for {sector} at {maturity} maturity]

## Cloud Strategy
[3-4 bullet points: cloud provider recommendation (AWS/Azure/GCP), migration approach, hybrid considerations specific to {sector}]

## Phase 1: Stabilise & Assess (Months 1-3)
[4-5 bullet points: tech debt assessment, cloud foundation, security baseline, quick wins]

## Phase 2: Modernise Core (Months 4-10)
[4-5 bullet points: application modernisation, API layer, data platform, DevOps/CI-CD]

## Phase 3: Innovate & Scale (Months 11-18)
[3-4 bullet points: AI/ML deployment, advanced analytics, automation, emerging tech pilots]

## AI & Data Priorities
[4-5 bullet points: specific AI use cases for {sector}, data platform architecture, analytics capabilities]

## Cybersecurity & Compliance
[3-4 bullet points: sector-specific security requirements, zero trust, regulatory compliance ({sector} regulations)]

## Technology Stack Recommendations
[5-6 bullet points: specific tools and platforms recommended for {sector} — cloud, data, integration, security]

## Risks & Mitigations
[4 bullet points: technical debt, talent, vendor lock-in, security risks]

Be highly specific to {sector}. Use technical terminology throughout.""",
}


def generate_module(
    company: str,
    sector: str,
    maturity: str,
    module_type: str,
    context: dict,
) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "⚠️ GROQ_API_KEY not found in .env file. Please add it and restart."

    prompt_template = PROMPTS.get(module_type, "")
    prompt = prompt_template.format(
        company=company,
        sector=sector,
        maturity=maturity,
        module_context=context.get(module_type, ""),
    )

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior transformation consultant producing structured, professional roadmaps. Use markdown ## headers exactly as instructed. Be specific with timelines, tools, and sector context. Never use generic filler — every point should be actionable and relevant."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.35,
            max_tokens=1400,
        )
        return response.choices[0].message.content
    except ImportError:
        return "⚠️ Groq not installed. Run: pip install groq"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
