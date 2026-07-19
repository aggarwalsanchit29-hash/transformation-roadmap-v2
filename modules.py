"""
modules.py
----------
Sector configs, maturity levels, and context for the AI generation layer.
"""

SECTORS = {
    "Banking & Financial Services": {
        "icon": "🏦", "color": "#3b82f6",
        "erp_context": "Core banking platforms, regulatory reporting (IFRS9, Basel IV), finance transformation, treasury management",
        "crm_context": "Relationship banking, wealth management client journeys, complaints management, cross-sell/upsell",
        "tech_context": "Cloud migration from legacy mainframes, open banking APIs, AI fraud detection, real-time payments infrastructure",
    },
    "Healthcare": {
        "icon": "🏥", "color": "#10b981",
        "erp_context": "NHS finance systems, procurement transformation, workforce management, ESR integration",
        "crm_context": "Patient relationship management, referral management, community health outreach, PALS",
        "tech_context": "EPR (Electronic Patient Record) deployment, interoperability (FHIR/HL7), AI diagnostics, telehealth",
    },
    "Retail & FMCG": {
        "icon": "🛒", "color": "#f59e0b",
        "erp_context": "Retail ERP, omnichannel inventory management, supply chain optimisation, merchandising",
        "crm_context": "Loyalty programme CRM, personalisation engine, customer 360, marketing automation",
        "tech_context": "E-commerce platform modernisation, AI demand forecasting, store technology, last-mile delivery",
    },
    "Energy & Utilities": {
        "icon": "⚡", "color": "#f97316",
        "erp_context": "Asset management (EAM), regulatory compliance, project accounting, field service management",
        "crm_context": "Smart meter customer journeys, EV proposition, green tariff management, vulnerability support",
        "tech_context": "Smart grid technology, IoT sensor networks, AI predictive maintenance, SCADA modernisation",
    },
    "Public Sector": {
        "icon": "🏛️", "color": "#8b5cf6",
        "erp_context": "Government ERP (Oracle Fusion, SAP), shared services, budget management, procurement reform",
        "crm_context": "Citizen engagement platforms, case management, multi-channel service delivery, self-service portals",
        "tech_context": "GDS/GOV.UK integration, cloud-first strategy (G-Cloud), legacy migration, cybersecurity",
    },
    "Manufacturing & Industrials": {
        "icon": "⚙️", "color": "#64748b",
        "erp_context": "SAP S/4HANA manufacturing, production planning, quality management, plant maintenance",
        "crm_context": "B2B sales CRM, dealer/distributor management, aftermarket services, warranty management",
        "tech_context": "Industry 4.0, IoT/IIoT, digital twin, MES integration, predictive quality analytics",
    },
}

MATURITY_LEVELS = {
    "Early Stage (Ad-hoc)": {
        "pct": 15,
        "next": "Developing",
        "description": "Fragmented systems, manual processes, limited integration",
    },
    "Developing (Defined)": {
        "pct": 40,
        "next": "Established",
        "description": "Some standardisation, partial integration, growing capability",
    },
    "Established (Managed)": {
        "pct": 65,
        "next": "Advanced",
        "description": "Standardised processes, integrated systems, data-driven decisions",
    },
    "Advanced (Optimising)": {
        "pct": 85,
        "next": "Leading",
        "description": "Optimised operations, AI-enabled, continuous improvement culture",
    },
}


def get_module_context(sector: str, maturity: str) -> dict:
    sector_data = SECTORS.get(sector, {})
    return {
        "erp": sector_data.get("erp_context", ""),
        "crm": sector_data.get("crm_context", ""),
        "tech": sector_data.get("tech_context", ""),
        "maturity": MATURITY_LEVELS.get(maturity, {}).get("description", ""),
    }
