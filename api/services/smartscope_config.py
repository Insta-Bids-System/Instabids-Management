"""Domain specific configuration for SmartScope AI prompting."""

from __future__ import annotations

from typing import Dict, List

CATEGORY_CONTEXT: Dict[str, Dict[str, List[str]]] = {
    "Plumbing": {
        "focus": [
            "Identify leak sources, corrosion, and water damage",
            "Call out fixture types and connection materials",
            "Note shutoff accessibility and isolation requirements",
        ],
        "materials": [
            "Common pipe diameters and materials",
            "Sealants, washers, traps, and valves",
        ],
    },
    "Electrical": {
        "focus": [
            "Highlight safety risks such as exposed conductors",
            "Describe device types (outlets, breakers, panels)",
            "Reference likely code compliance issues",
        ],
        "materials": [
            "Replacement devices, covers, wiring gauges",
            "Protective equipment requirements",
        ],
    },
    "Hvac": {
        "focus": [
            "Capture equipment make, model, and age indicators",
            "Inspect duct connections, condensate lines, and filters",
            "Check thermostat status and control wiring",
        ],
        "materials": [
            "Filters, sealants, refrigerant handling items",
            "Fasteners, insulation, and drain treatments",
        ],
    },
    "Roofing": {
        "focus": [
            "Identify shingle, flashing, or decking damage",
            "Call out water intrusion paths and structural risks",
            "Assess guttering and drainage conditions",
        ],
        "materials": [
            "Shingle types, fasteners, sealants",
            "Safety equipment for working at height",
        ],
    },
    "General Maintenance": {
        "focus": [
            "Document surface damage, wear, and cosmetic issues",
            "Identify appliance or fixture model information",
            "Highlight safety or habitability concerns",
        ],
        "materials": [
            "Paints, drywall products, flooring supplies",
            "Cleaning or remediation materials",
        ],
    },
}


CATEGORY_SCOPE_TEMPLATES: Dict[str, List[str]] = {
    "Plumbing": [
        "Isolate water supply and verify shutoff valves are functional",
        "Remove damaged components and inspect for secondary leaks",
        "Install replacement parts and pressure test the system",
    ],
    "Electrical": [
        "De-energise the affected circuit and confirm lockout",
        "Replace or repair damaged devices and wiring",
        "Test circuit continuity and restore service with verification",
    ],
    "Hvac": [
        "Perform system diagnostics and capture error codes",
        "Service or replace impacted components",
        "Run performance test across cooling and heating modes",
    ],
    "Roofing": [
        "Install safety equipment and assess working conditions",
        "Remove compromised roofing materials and inspect substrate",
        "Install new materials ensuring watertight seals",
    ],
    "General Maintenance": [
        "Prepare workspace and protect adjacent finishes",
        "Repair or replace damaged components",
        "Restore area to original condition and clean up",
    ],
}


SYSTEM_PROMPT = """
You are SmartScope AI, an assistant that analyses property maintenance photos for a marketplace
connecting property managers with contractors. Provide detailed, standardised scopes of work that
contractors can execute without visiting the site. The response must be valid JSON following the
provided schema and include measurable details. Always state uncertainty explicitly and request
additional photos if confidence is low.
""".strip()


def build_category_guidance(category: str) -> str:
    """Generate a human readable guidance string for the prompt."""

    config = CATEGORY_CONTEXT.get(
        category, CATEGORY_CONTEXT.get("General Maintenance", {})
    )
    focus = "\n".join(f"- {item}" for item in config.get("focus", []))
    materials = "\n".join(f"- {item}" for item in config.get("materials", []))

    return (
        f"Category Guidance ( {category} ):\n"
        f"Focus Areas:\n{focus or '- Tailor analysis to visible defects and context'}\n"
        f"Material Insights:\n{materials or '- Recommend high confidence material matches'}"
    )


__all__ = [
    "CATEGORY_CONTEXT",
    "CATEGORY_SCOPE_TEMPLATES",
    "SYSTEM_PROMPT",
    "build_category_guidance",
]
