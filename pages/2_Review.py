"""
"Did we get this right?" page — The Route

Plain-language playback of what the system understood from intake, shown
before any output is generated. Per UI Flow v2 this is the most important
screen — it catches assumption failures before they propagate.

Deliberately NO AI on this page. The playback is assembled from the
parent's actual answers by plain code, so what they confirm is exactly
what the system has — nothing paraphrased, nothing invented.

Also runs deterministic contradiction checks (e.g. age 16 + "aged out")
and surfaces them as flags the parent can resolve before continuing.

Three CTAs: This is right / Edit something / Add a note.
"""

import streamlit as st

from lib.profile import hydrate_session_state, set_confirmed, save_note

st.set_page_config(page_title="Did we get this right? — The Route", layout="centered")
hydrate_session_state()


# ─────────────────────────────────────────────
# Guard: profile must exist
# ─────────────────────────────────────────────
profile = st.session_state.get("profile")

if not profile:
    st.title("We need to hear about your young person first.")
    st.write("This page plays back what we understood from your intake. Without the intake there's nothing to play back.")
    st.page_link("pages/1_Intake.py", label="Go to the intake →")
    st.stop()


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _val(key: str) -> str:
    v = profile.get(key)
    if v in (None, "", "—", []):
        return ""
    return str(v).strip()


def _list(key: str) -> list:
    v = profile.get(key)
    return v if isinstance(v, list) else []


def _quote(text: str) -> str:
    """Render the parent's own words as an indented quote."""
    return "\n".join("> " + line for line in text.splitlines() if line.strip())


name = _val("their_name") or "your young person"
age = profile.get("their_age")
state = _val("state")
school = _val("school_status")


# ─────────────────────────────────────────────
# Contradiction checks — deterministic, no AI
# ─────────────────────────────────────────────
flags = []

if school == "Recently aged out, nothing in place yet" and isinstance(age, int) and age <= 17:
    flags.append(
        f"You said {name} is **{age}**, and also that they've **aged out of school services**. "
        "Those don't usually go together — school services run to 21 in New Jersey and 22 in New York. "
        "If one of these is off, hit **Edit something** below."
    )

if school == "Still in high school (with an IEP)" and isinstance(age, int) and age >= 23:
    flags.append(
        f"You said {name} is **{age}** and still in high school with an IEP. "
        "IEP services typically end at 21 (NJ) or 22 (NY) — if one of these is off, "
        "hit **Edit something** below."
    )

diagnoses = _list("diagnoses")
if diagnoses == ["No Formal Diagnosis"]:
    flags.append(
        f"You said {name} has **no formal diagnosis**. Good to know — many of the programs "
        "we cover require one to qualify, so what you get next will factor that in. "
        "If there is a diagnosis we missed, hit **Edit something**."
    )


# ─────────────────────────────────────────────
# Playback sections
# ─────────────────────────────────────────────
sections: list[tuple[str, list[str]]] = []

# About them
about = []
if age and state:
    about.append(f"**{name}** is **{age}**, and you're in **{state}**.")
elif age:
    about.append(f"**{name}** is **{age}**.")
if state == "New Jersey" and _val("nj_county"):
    about.append(f"County: {_val('nj_county')}.")
if state == "New York" and _val("ny_region"):
    about.append(f"Region: {_val('ny_region')}.")
if state == "Other" and _val("other_state"):
    about.append(
        f"You're in **{_val('other_state')}**. Our deep state-level guidance covers "
        "New Jersey and New York right now, so what you get will lean on the federal programs."
    )

if diagnoses:
    about.append("Diagnoses you checked: " + ", ".join(diagnoses) + ".")
    if _val("diagnoses_other"):
        about.append(f"You added: {_val('diagnoses_other')}")
if _val("communication"):
    about.append(f"How they communicate: {_val('communication').lower()}.")
sections.append((f"About {name}", about))

# In the parent's words
words = []
for label, key in [
    ("Their main challenges", "primary_challenges"),
    ("On their best day", "best_day_challenges"),
    ("On their worst day", "worst_day_challenges"),
    ("Their strengths", "primary_strengths"),
    ("What they love", "what_they_love"),
    ("What they hate", "what_they_hate"),
    ("What they're great at", "what_great_at"),
    ("Where they struggle", "where_they_struggle"),
]:
    if _val(key):
        words.append(f"**{label}**, in your words:")
        words.append(_quote(_val(key)))
sections.append(("What you told us about who they are", words))

# School & what's next
standing = []
if school:
    standing.append(f"School-wise: **{school}**.")
gm, gy = _val("grad_month"), _val("grad_year")
if gm and gm != "Not sure" and gy and gy != "Not sure":
    standing.append(f"Expected to graduate or age out: **{gm} {gy}**.")
if _val("whats_next"):
    standing.append(f"What {name} wants next, in your words:")
    standing.append(_quote(_val("whats_next")))
if _val("good_options"):
    standing.append("Options that seem right to you:")
    standing.append(_quote(_val("good_options")))

considering = _list("considering")
if considering:
    standing.append("**Paths on the table:**")
    standing.extend(f"- {c}" for c in considering)
    if _val("considering_other"):
        standing.append(f"- {_val('considering_other')}")
followup_bits = []
if _val("college_idd_program"):
    followup_bits.append(f"Specialized IDD program at the college: {_val('college_idd_program').lower()}")
if _val("community_college_time"):
    followup_bits.append(f"Community college: {_val('community_college_time').lower()}")
if _val("transition_program_type"):
    followup_bits.append(f"Transition program: {_val('transition_program_type').lower()}")
if _val("college_location"):
    followup_bits.append(f"School location: {_val('college_location').lower()}")
if followup_bits:
    standing.append("Details: " + " · ".join(followup_bits) + ".")
sections.append(("Where things stand", standing))

# Transition pieces — grouped by status
pieces = profile.get("transition_pieces") or {}
context = profile.get("transition_context") or {}
piece_lines = []
for status, header in [
    ("Accepted", "**Accepted:**"),
    ("Pending", "**Pending:**"),
    ("Rejected", "**Rejected:**"),
    ("Not started", "**Not started:**"),
    ("Not sure", "**Not sure:**"),
    # Legacy v0.2 statuses, so old profiles still play back
    ("Done", "**Done:**"),
    ("Unnecessary", "**You marked as not needed:**"),
]:
    items = [label for label, s in pieces.items() if s == status]
    if items:
        piece_lines.append(header)
        for label in items:
            extra = f" — {context[label].lower()}" if context.get(label) else ""
            piece_lines.append(f"- {label}{extra}")

legal = _list("legal_stack")
if legal:
    in_place = [x for x in legal if x not in ("Not started", "In progress")]
    if in_place:
        piece_lines.append("**Legal paperwork in place:** " + ", ".join(in_place) + ".")
    if "In progress" in legal:
        piece_lines.append("Legal paperwork: more in progress.")
    if "Not started" in legal and not in_place:
        piece_lines.append("**Legal paperwork:** not started.")
    if _val("legal_route"):
        piece_lines.append(f"How you did it: {_val('legal_route')}")
if _val("transition_catch_all"):
    piece_lines.append("You also flagged:")
    piece_lines.append(_quote(_val("transition_catch_all")))
if _val("insurance"):
    piece_lines.append(f"Health insurance: **{_val('insurance')}**.")
sections.append(("The big transition pieces", piece_lines))

# What you've tried
tried = []
if _val("tried_working"):
    tried.append("Working:")
    tried.append(_quote(_val("tried_working")))
if _val("tried_not_working"):
    tried.append("Didn't fit or didn't work:")
    tried.append(_quote(_val("tried_not_working")))
sections.append(("What you've tried so far", tried))

# Who's around
around = []
if _list("support_network"):
    around.append("Day to day: " + ", ".join(_list("support_network")) + ".")
past = [p for p in _list("worked_with_past") if p != "None of the above"]
current = [p for p in _list("worked_with_current") if p != "None of the above"]
if current:
    around.append("Currently working with: " + ", ".join(current) + ".")
if past:
    around.append("Have worked with before: " + ", ".join(past) + ".")
if not past and not current and (_list("worked_with_past") or _list("worked_with_current")):
    around.append("You haven't worked with advocates, attorneys, or coordinators yet.")
# Legacy v0.2 field
if _list("professionals") and not (past or current):
    pros = [p for p in _list("professionals") if p != "None of the above"]
    if pros:
        around.append("You've worked with: " + ", ".join(pros) + ".")
sections.append(("Who's around you", around))

# What's on the parent's mind
mind = []
if _val("next_six_months"):
    mind.append("Coming up in the next six months:")
    mind.append(_quote(_val("next_six_months")))
if _val("keeping_up_at_night"):
    mind.append("What's keeping you up at night:")
    mind.append(_quote(_val("keeping_up_at_night")))
if _val("todo_list"):
    mind.append("Your to-do list right now:")
    mind.append(_quote(_val("todo_list")))
if _val("parent_note"):
    mind.append("Your added note:")
    mind.append(_quote(_val("parent_note")))
sections.append(("What's on your mind", mind))


# ─────────────────────────────────────────────
# Render
# ─────────────────────────────────────────────
st.title("Did we get this right?")
st.write(
    f"Before we tell you anything, here's what we understood about {name} and your "
    "family. Everything you get next builds on this — if something's off, fix it now."
)

for flag in flags:
    st.warning(flag)

st.write("---")

for header, lines in sections:
    if not lines:
        continue
    st.subheader(header)
    st.markdown("\n\n".join(lines))
    st.write("")

st.write("---")


# ─────────────────────────────────────────────
# CTAs: This is right / Edit something / Add a note
# ─────────────────────────────────────────────
col_a, col_b, col_c = st.columns(3)

with col_a:
    if st.button("This is right", type="primary"):
        st.session_state["confirmed"] = True
        set_confirmed()
        st.switch_page("pages/3_Snapshot.py")

with col_b:
    if st.button("Edit something"):
        st.switch_page("pages/1_Intake.py")

with col_c:
    if st.button("Add a note"):
        st.session_state["adding_note"] = True

if st.session_state.get("adding_note"):
    note = st.text_area(
        "What should we know?",
        help="Anything we missed, got wrong, or should weigh differently.",
        height=120,
    )
    if st.button("Save note"):
        if note.strip():
            save_note(note.strip())
            st.session_state["adding_note"] = False
            st.success("Added. We'll read it alongside everything else.")
            st.rerun()
