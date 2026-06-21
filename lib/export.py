"""
Export helper for The Route — testing phase.

Builds a single readable text file of a parent's intake answers (and, if
they've gotten that far, their Snapshot and Next Steps) so a solo tester can
download it and email it to Michele. Nothing is stored server-side; the parent
chooses to send it. Privacy stays clean.

Remove or gate this once real persistence + accounts exist (Phase 2).
"""

from __future__ import annotations

# Human-readable labels for the v0.4 profile keys, in intake order.
# Anything not in this map is skipped from the readable view (it still
# appears in the raw block at the bottom).
_LABELS: list[tuple[str, str]] = [
    ("your_name", "Your first name"),
    ("relationship", "Who you are to them"),
    ("relationship_other", "  (other)"),
    ("their_name", "Their first name"),
    ("their_age", "Their age"),
    ("diagnoses", "Diagnoses"),
    ("diagnoses_other", "  (other diagnosis)"),
    ("communication", "How they communicate"),
    ("associated_challenges", "Associated challenges"),
    ("challenges_everyday", "What that looks like day to day"),
    ("strategies_worked", "Strategies that have worked"),
    ("strategies_not_worked", "Strategies that didn't work"),
    ("strengths", "Strengths"),
    ("where_they_shine", "Where else they shine"),
    ("anything_else", "Anything else about them"),
    ("state", "State"),
    ("nj_county", "  County"),
    ("ny_region", "  Region"),
    ("other_state", "  State (other)"),
    ("support_network", "Who's around day to day"),
    ("education_status", "Current educational status"),
    ("current_program", "  Which program / where"),
    ("hs_type", "  High school type"),
    ("hs_year", "  Current year"),
    ("hs_plan", "  IEP or 504"),
    ("postsec_stage", "  Postsecondary stage"),
    ("education_other", "  (other / unsure)"),
    ("grad_date", "Expected graduation / age-out date"),
    ("transition_pieces", "Big transition pieces — status"),
    ("transition_context", "  who's driving / why"),
    ("legal_stack", "Legal paperwork in place"),
    ("legal_route", "  how it was done"),
    ("transition_catch_all", "Other notes on legal/benefits/services"),
    ("insurance", "Health insurance"),
    ("worked_with_past", "Have worked with"),
    ("worked_with_current", "Currently work with"),
    ("worked_with_other", "  (someone else)"),
    ("considering", "Next steps considering"),
    ("considering_other", "  (other)"),
    ("college_idd_program", "  College IDD program?"),
    ("community_college_time", "  Community college enrollment"),
    ("transition_program_type", "  Transition program type"),
    ("college_location", "  School location"),
    ("next_six_months", "Worried about in next six months"),
    ("keeping_up_at_night", "Keeping you up at night"),
    ("todo_list", "On your to-do list now"),
    ("parent_note", "Added note"),
]


def _fmt(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return "; ".join(f"{k}: {v}" for k, v in value.items())
    return str(value)


def _is_empty(value) -> bool:
    return value in (None, "", "—", [], {})


def build_export_text(profile: dict, snapshot: str = "", next_steps: str = "") -> str:
    """Return a plain-text export of everything the parent produced."""
    profile = profile or {}
    lines: list[str] = []
    lines.append("THE ROUTE — TEST SESSION RESPONSES")
    lines.append("Please email this file to mkunken@gmail.com")
    lines.append("=" * 60)
    lines.append("")
    lines.append("PART 1 — YOUR INTAKE ANSWERS")
    lines.append("-" * 60)

    seen = set()
    for key, label in _LABELS:
        seen.add(key)
        val = profile.get(key)
        if _is_empty(val):
            continue
        lines.append(f"{label}: {_fmt(val)}")

    # Any keys not covered by the label map, so nothing is silently lost.
    _hidden = {"intake_version"}
    extras = {
        k: v for k, v in profile.items()
        if k not in seen and k not in _hidden and not _is_empty(v)
    }
    if extras:
        lines.append("")
        lines.append("Other captured fields:")
        for k, v in extras.items():
            lines.append(f"{k}: {_fmt(v)}")

    if snapshot:
        lines.append("")
        lines.append("=" * 60)
        lines.append("PART 2 — THE SNAPSHOT YOU SAW")
        lines.append("-" * 60)
        lines.append(snapshot.strip())

    if next_steps:
        lines.append("")
        lines.append("=" * 60)
        lines.append("PART 3 — THE NEXT STEPS YOU SAW")
        lines.append("-" * 60)
        lines.append(next_steps.strip())

    lines.append("")
    return "\n".join(lines)
