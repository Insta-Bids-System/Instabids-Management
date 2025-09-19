"""Configuration for SmartScope AI prompting and categorisation."""

from __future__ import annotations

from typing import Dict, List

# Guidance templates for different maintenance categories
CATEGORY_GUIDANCE: Dict[str, str] = {
    "Plumbing": """
For plumbing issues:
- Identify the specific plumbing system affected (supply, drainage, fixtures)
- Note water damage risks and containment needs
- Assess urgency based on water flow and damage potential
- Consider code compliance requirements for repairs
- Evaluate access challenges (walls, crawl spaces, etc.)
""".strip(),
    "Electrical": """
For electrical issues:
- Prioritise safety - note any exposed wiring or electrical hazards
- Identify circuit types and amperage requirements
- Note compliance needs with local electrical codes
- Consider permit requirements for significant work
- Assess panel capacity for new circuits or upgrades
""".strip(),
    "HVAC": """
For HVAC systems:
- Identify system type (central air, heat pump, boiler, etc.)
- Note seasonal urgency and tenant comfort impact
- Assess filter access and replacement schedules
- Consider energy efficiency opportunities
- Evaluate ductwork access and condition
""".strip(),
    "Roofing": """
For roofing issues:
- Assess weather exposure and urgency
- Note structural integrity and safety concerns
- Identify roofing material type and age
- Consider access challenges and safety equipment needs
- Evaluate drainage and guttering systems
""".strip(),
    "Flooring": """
For flooring issues:
- Identify flooring material and subfloor condition
- Note safety hazards (trip risks, loose materials)
- Assess moisture damage and mold risks
- Consider tenant disruption during repairs
- Evaluate matching materials for partial replacements
""".strip(),
    "Appliances": """
For appliance issues:
- Identify make, model, and age of appliance
- Note safety concerns (gas leaks, electrical hazards)
- Assess repair vs replacement cost-effectiveness
- Consider warranty status and service availability
- Evaluate installation requirements and permits
""".strip(),
    "General Maintenance": """
For general maintenance:
- Assess overall property condition and safety
- Note any code violations or compliance issues
- Consider preventive maintenance opportunities
- Evaluate tenant impact and scheduling needs
- Identify related systems that may need attention
""".strip(),
}

# Recommended scope templates by category
CATEGORY_SCOPE_TEMPLATES: Dict[str, List[str]] = {
    "Plumbing": [
        "Shut off water supply to affected area",
        "Assess extent of water damage",
        "Remove and replace damaged components",
        "Test system for leaks and proper operation",
        "Restore water service and clean up work area",
    ],
    "Electrical": [
        "Turn off power at circuit breaker",
        "Test circuits and identify issues",
        "Replace or repair electrical components",
        "Install new wiring per code requirements",
        "Test system and restore power",
    ],
    "HVAC": [
        "Diagnose system operation and performance",
        "Replace filters and clean components",
        "Repair or replace faulty parts",
        "Test system operation and airflow",
        "Schedule regular maintenance follow-up",
    ],
    "Roofing": [
        "Inspect roof structure and materials",
        "Remove damaged roofing materials",
        "Install new roofing and flashing",
        "Seal and weatherproof installation",
        "Clean up debris and test drainage",
    ],
    "Flooring": [
        "Remove damaged flooring materials",
        "Inspect and repair subfloor if needed",
        "Install new flooring materials",
        "Trim and finish installation",
        "Clean and protect new flooring",
    ],
    "Appliances": [
        "Disconnect and remove old appliance",
        "Prepare installation area",
        "Install new appliance and connections",
        "Test operation and safety features",
        "Provide warranty and maintenance information",
    ],
    "General Maintenance": [
        "Assess overall condition and safety",
        "Complete necessary repairs and improvements",
        "Test all affected systems",
        "Clean and restore work areas",
        "Document completed work and recommendations",
    ],
}

SYSTEM_PROMPT = """
You are SmartScope AI, an assistant that analyses property maintenance photos for a marketplace
connecting property managers with contractors. Provide detailed, standardised scopes of work
that help contractors submit accurate bids.

Your analysis should be:
- Specific and actionable for contractors
- Based on what's visible in the photos
- Realistic about time and material estimates
- Safety-conscious and code-compliant
- Clear about uncertainties and assumptions

Focus on creating scope items that contractors can easily understand and bid on accurately.
""".strip()


def build_category_guidance(category: str) -> str:
    """Build category-specific guidance text for prompting."""
    return CATEGORY_GUIDANCE.get(category, CATEGORY_GUIDANCE["General Maintenance"])


__all__ = [
    "CATEGORY_GUIDANCE",
    "CATEGORY_SCOPE_TEMPLATES", 
    "SYSTEM_PROMPT",
    "build_category_guidance",
]