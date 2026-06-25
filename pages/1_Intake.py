"""
Intake page — The Route
v0.4 questionnaire (June 20, 2026 spec) — UX pass June 21.

UX pass changes (from live testing feedback):
- Helper / commentary now VISIBLE under each question (st.caption), not hidden
  behind "?" tooltips.
- "What are you considering" (Q17) is now visible checkboxes under warm,
  non-binary group labels — not collapsed "Choose options" dropdowns, and no
  more "Not college".
- Legal paperwork is visible checkboxes nested clearly under Q14, so it stops
  reading as its own section.
- The transition matrix (Q14) no longer stacks a follow-up question under every
  row (that caused the "every other line" clutter). Status only; nuance goes in
  the catch-all box.

No st.form — conditional follow-ups need live reruns. Widgets hold their own
state via keys; the save button at the bottom assembles the profile. Pre-fills
from the saved profile so "Edit something" returns the parent to their answers.
"""

import streamlit as st

from lib.profile import save_profile, hydrate_session_state
from lib.export import build_export_text

st.set_page_config(page_title="Intake — The Route", layout="centered")
hydrate_session_state()

# Existing answers, if any — used to pre-fill widgets on first render.
_p = st.session_state.get("profile") or {}


def _idx(options: list, key: str, default: int = 0) -> int:
    v = _p.get(key)
    return options.index(v) if v in options else default


def _txt(key: str) -> str:
    v = _p.get(key)
    return v if isinstance(v, str) else ""


def _picked(options: list, key: str) -> list:
    v = _p.get(key)
    return [x for x in v if x in options] if isinstance(v, list) else []


def q(text: str, helper: str = "") -> None:
    """Render a question label and (optional) visible helper text, with breathing room above."""
    st.markdown("<div style='margin-top: 1.6rem'></div>", unsafe_allow_html=True)
    st.markdown(f"**{text}**")
    if helper:
        st.caption(helper)


def checkbox_group(options: list, saved_keys: list, key_prefix: str) -> list:
    """Render a vertical list of visible checkboxes. Returns the checked ones."""
    chosen = []
    for i, opt in enumerate(options):
        if st.checkbox(opt, value=(opt in saved_keys), key=f"{key_prefix}_{i}"):
            chosen.append(opt)
    return chosen


# ─────────────────────────────────────────────
# Welcome / what to expect
# ─────────────────────────────────────────────
st.title("Let's get the full picture.")
st.write(
    "Tell us about your kid and where everything stands. This takes about **15 to 30 minutes**. "
    "Your answers are private — they stay in your own browser and are never shared with anyone, "
    "including other families using this. It's best to finish in one sitting. "
    "Some questions are multiple choice, some are write-in — take as much space as you need. "
    "The more we know, the more we can help."
)
if _p:
    st.info("Your earlier answers are filled in below. Change whatever needs changing and save again.")
st.write("---")

# ─────────────────────────────────────────────
# Section 1: About you
# ─────────────────────────────────────────────
st.header("About you")

q("Q1. What's your first name?", "We'll use it when it makes sense. This all stays on your computer.")
your_name = st.text_input("Q1", value=_txt("your_name"), label_visibility="collapsed")

_relationship_opts = [
    "Parent",
    "Grandparent",
    "Sibling",
    "Foster or kinship caregiver",
    "Aunt / uncle",
    "Other",
]
q("Q2. Who are you to them?")
relationship = st.selectbox(
    "Q2",
    options=_relationship_opts,
    index=_idx(_relationship_opts, "relationship"),
    label_visibility="collapsed",
)
relationship_other = ""
if relationship == "Other":
    relationship_other = st.text_input(
        "Tell us who you are to them:",
        value=_txt("relationship_other"),
        key="relationship_other",
    )

st.write("---")

# ─────────────────────────────────────────────
# Section 2: Describe your kid
# ─────────────────────────────────────────────
st.header("Describe your kid")

q("Q3. What's their first name?")
their_name = st.text_input("Q3", value=_txt("their_name"), label_visibility="collapsed")

_age_opts = list(range(16, 27))
q("Q4. How old are they?")
their_age = st.selectbox(
    "Q4",
    options=_age_opts,
    index=_age_opts.index(_p["their_age"]) if _p.get("their_age") in _age_opts else 0,
    label_visibility="collapsed",
)

_diagnosis_opts = [
    "ADHD",
    "Anxiety",
    "Autism",
    "Bipolar Disorder",
    "Central Auditory Processing Disorder (CAPD)",
    "Cerebral Palsy",
    "Depression",
    "Down Syndrome",
    "Dyscalculia",
    "Dysgraphia",
    "Dyslexia",
    "Fetal alcohol syndrome / FASD",
    "Intellectual disability",
    "OCD",
    "PTSD / Trauma history",
    "Sensory Processing Issues",
    "Traumatic brain injury",
    "No Formal Diagnosis",
    "Something Else",
]
q("Q5. Have they been diagnosed with a disability?", "Check all that apply.")
_diag_saved = _picked(_diagnosis_opts, "diagnoses")
diagnoses = []
_dcol1, _dcol2 = st.columns(2)
_dhalf = (len(_diagnosis_opts) + 1) // 2
for _di, _dopt in enumerate(_diagnosis_opts):
    with (_dcol1 if _di < _dhalf else _dcol2):
        if st.checkbox(_dopt, value=(_dopt in _diag_saved), key=f"diag_{_di}"):
            diagnoses.append(_dopt)
diagnoses_other = ""
if "Something Else" in diagnoses:
    diagnoses_other = st.text_input(
        "Tell us more about the diagnosis:",
        value=_txt("diagnoses_other"),
        key="diagnoses_other",
    )

_communication_opts = [
    "Speaks fluently",
    "Speaks, but with limits or support",
    "Uses AAC, sign, or another tool",
    "Nonverbal",
]
q("Q6. How do they communicate, mostly?")
communication = st.radio(
    "Q6",
    options=_communication_opts,
    index=_idx(_communication_opts, "communication"),
    label_visibility="collapsed",
)

q(
    "Q7. What are their associated challenges?",
    "Here we're looking for the kinds of terms you'd find on a clinical evaluation, like "
    "\"executive functioning\" or \"mood regulation disorder.\" If you don't have this information, "
    "just tell us the challenges in your own words — like \"has a hard time with organization\" or "
    "\"is very impulsive.\"",
)
associated_challenges = st.text_area(
    "Q7", value=_txt("associated_challenges"), label_visibility="collapsed", height=120
)

q(
    "Q7a. What does this look like in everyday life?",
    "What kinds of situations are challenging for your kid? How do they respond? For example, if "
    "your kid has social / pragmatic speech issues, what situations are problematic and what does "
    "your kid do as a result (shut down, become confrontational, etc.)? Be as descriptive and "
    "specific as possible.",
)
challenges_everyday = st.text_area(
    "Q7a", value=_txt("challenges_everyday"), label_visibility="collapsed", height=120
)

q(
    "Q7b. What strategies have you tried that have worked for them?",
    "Think PT, OT, DBT, social skills classes, life skills, other organized or informal activities or strategies.",
)
strategies_worked = st.text_area(
    "Q7b", value=_txt("strategies_worked"), label_visibility="collapsed", height=120
)

q(
    "Q7c. What strategies have you tried that didn't fit or didn't work?",
    "Anything we shouldn't suggest again because you've already been there?",
)
strategies_not_worked = st.text_area(
    "Q7c", value=_txt("strategies_not_worked"), label_visibility="collapsed", height=120
)

q(
    "Q8. What are their strengths?",
    "We're looking for the kind of thing you'd find in a psych or educational eval, like \"excellent "
    "working memory\" or \"strong inferential reasoning.\" If you don't have this information, just tell "
    "us the strengths in your own words — like \"can look at something once and memorize it\" or \"is "
    "very organized.\"",
)
strengths = st.text_area("Q8", value=_txt("strengths"), label_visibility="collapsed", height=120)

q(
    "Q9. Where else do they shine?",
    "Be as descriptive and specific as possible. Is your kid kind and dependable? Exceptionally "
    "organized or funny? An artist? A math whiz? Amazing at improv? Tell us everything.",
)
where_they_shine = st.text_area(
    "Q9", value=_txt("where_they_shine"), label_visibility="collapsed", height=120
)

q(
    "Q10. Anything else you want to tell us about your kid's challenges, strengths, interests, and/or skills?",
    "Keep in mind we're going to ask you about hopes and dreams — and dig into specific transition goals — later.",
)
anything_else = st.text_area(
    "Q10", value=_txt("anything_else"), label_visibility="collapsed", height=120
)

st.write("---")

# ─────────────────────────────────────────────
# Section 3: Where you live
# ─────────────────────────────────────────────
st.header("Where you live")

_state_opts = ["New Jersey", "New York", "Other"]
q("Q11. What state are you in?")
state = st.selectbox(
    "Q11",
    options=_state_opts,
    index=_idx(_state_opts, "state"),
    label_visibility="collapsed",
)
nj_county = ""
ny_region = ""
other_state = ""
if state == "New Jersey":
    nj_county = st.text_input("What county?", value=_txt("nj_county"), key="nj_county")
elif state == "New York":
    _ny_region_opts = [
        "—",
        "NYC",
        "Long Island",
        "Hudson Valley",
        "Western NY",
        "Capital Region",
        "Central NY",
        "North Country",
        "Southern Tier",
        "Finger Lakes",
    ]
    ny_region = st.selectbox(
        "What region?",
        options=_ny_region_opts,
        index=_idx(_ny_region_opts, "ny_region"),
        key="ny_region",
    )
else:
    other_state = st.text_input("Which state?", value=_txt("other_state"), key="other_state")

st.write("---")

# ─────────────────────────────────────────────
# Section 4: Who's around you
# ─────────────────────────────────────────────
st.header("Who's around you")

_support_opts = [
    "Co-parent / other parent in the home",
    "Other parent (separated or co-parenting)",
    "Siblings (any age)",
    "Grandparents",
    "Paid support staff or aides",
    "Extended family",
    "It's mostly just me",
    "Other",
]
q("Q12. Who else is in the picture day-to-day?", "Check all that apply.")
support_network = checkbox_group(_support_opts, _picked(_support_opts, "support_network"), "support")

q("Q13. Who are you currently working with?", "Check anyone on your team right now.")
_professional_opts = [
    "A parent advocate",
    "A special-ed attorney",
    "A transition coordinator at the school",
    "A service coordinator (NJ DDD or NY OPWDD)",
    "A parent center (SPAN, INCLUDEnyc, Arc, etc.)",
    "A private case manager or planner",
    "A therapist for your kid",
    "An EF / executive function coach",
    "Something else",
    "None of the above",
]
worked_with_current = checkbox_group(_professional_opts, _picked(_professional_opts, "worked_with_current"), "wcur")
worked_with_past = []  # the "have worked with" column was dropped; keep the key empty for downstream compatibility
worked_with_other = ""
if "Something else" in worked_with_current:
    worked_with_other = st.text_input("Who else?", value=_txt("worked_with_other"), key="worked_with_other")

st.write("---")

# ─────────────────────────────────────────────
# Section 5: Where they are right now
# ─────────────────────────────────────────────
st.header("School, services & legal")

_education_opts = [
    "High School",
    "18–21 Transition Program",
    "Vocational Program",
    "College or postsecondary program",
    "Graduated or aged out — nothing in place right now",
    "Something else / unsure",
]
q("Q14. What's their current educational status?")
education_status = st.radio(
    "Q13",
    options=_education_opts,
    index=_idx(_education_opts, "education_status"),
    label_visibility="collapsed",
)

hs_type = ""
hs_year = ""
hs_plan = ""
postsec_stage = ""
education_other = ""
current_program = ""
if education_status == "High School":
    _hs_type_opts = ["Public", "Private special education", "Boarding", "Day program", "Other"]
    hs_type = st.selectbox(
        "What type?",
        options=_hs_type_opts,
        index=_idx(_hs_type_opts, "hs_type"),
        key="hs_type",
    )
    hs_year = st.text_input("Current year (e.g., junior, senior):", value=_txt("hs_year"), key="hs_year")
    _hs_plan_opts = ["IEP", "504 plan", "Both", "Neither", "Not sure"]
    hs_plan = st.radio(
        "IEP or 504 plan?",
        options=_hs_plan_opts,
        index=_idx(_hs_plan_opts, "hs_plan"),
        horizontal=True,
        key="hs_plan",
    )
elif education_status == "College or postsecondary program":
    _postsec_opts = ["Entering this fall", "Already started / currently enrolled"]
    postsec_stage = st.radio(
        "Which is it?",
        options=_postsec_opts,
        index=_idx(_postsec_opts, "postsec_stage"),
        key="postsec_stage",
    )
elif education_status == "Something else / unsure":
    education_other = st.text_input(
        "Say more:",
        value=_txt("education_other"),
        key="education_other",
    )

if education_status in (
    "College or postsecondary program",
    "Vocational Program",
    "18–21 Transition Program",
):
    current_program = st.text_input(
        "Which one? Tell us the name — and where it is, if it's away from home.",
        value=_txt("current_program"),
        key="current_program",
    )

q("Q14a. Expected graduation or age-out date, if relevant:", "Month and year is fine. Leave blank if it doesn't apply.")
grad_date = st.text_input("Q13a", value=_txt("grad_date"), label_visibility="collapsed")

st.write("")
q(
    "Q15. Where do things stand on the big transition pieces?",
    "These are the benefits, services, and legal steps that take time to set up. Tell us where each "
    "one is — it's fine if the answer is \"haven't started\" or \"not sure what this is.\"",
)

_piece_status_opts = ["Accepted", "Pending", "Rejected", "Not started", "Ruled out", "Not sure"]
_piece_rows = [
    "Registered with the state's developmental disability agency (DDD in NJ, OPWDD in NY)",
    "Applied for SSI",
    "Connected to vocational rehab (DVRS in NJ, ACCES-VR in NY)",
    "Medicaid waiver applied for",
]
_legal_opts = [
    "HIPAA release",
    "FERPA waiver",
    "Financial POA",
    "Medical POA",
    "SDM agreement",
    "Full guardianship",
    "In progress",
    "Not started",
]
_saved_pieces = _p.get("transition_pieces") or {}
transition_pieces = {}
transition_context = {}  # follow-ups removed from the form; kept empty for downstream compatibility
legal_route = ""

# The whole transition picture lives in one bordered box so the legal
# paperwork reads as part of this question, not a separate section.
with st.container(border=True):
    for label in _piece_rows:
        transition_pieces[label] = st.radio(
            label,
            options=_piece_status_opts,
            index=_piece_status_opts.index(_saved_pieces[label]) if _saved_pieces.get(label) in _piece_status_opts else 3,
            horizontal=True,
            key=f"piece::{label}",
        )

    st.caption("And the legal & decision-making paperwork — check everything that's already in place.")
    legal_stack = checkbox_group(_legal_opts, _picked(_legal_opts, "legal_stack"), "legal")
    if any(item in legal_stack for item in _legal_opts[:6]):
        legal_route = st.text_input(
            "What route did you take? (e.g., Mama Bear forms, attorney, court)",
            value=_txt("legal_route"),
            key="legal_route",
        )

    st.caption("Anything else worth flagging about the legal, benefits, or services list?")
    transition_catch_all = st.text_area(
        "catch_all", value=_txt("transition_catch_all"), label_visibility="collapsed", height=100
    )

_insurance_opts = [
    "On a parent's private plan",
    "On Medicaid",
    "Both",
    "No insurance",
    "Not sure",
]
q("Q16. What's their health insurance situation?")
insurance = st.radio(
    "Q15",
    options=_insurance_opts,
    index=_idx(_insurance_opts, "insurance"),
    label_visibility="collapsed",
)

st.write("---")

# ─────────────────────────────────────────────
# Section 6: Where they are headed
# ─────────────────────────────────────────────
st.header("Looking ahead")
q(
    "Q17. What are you working toward?",
    "Check all that apply — more than one is fine. These can be goals, not just what's already decided.",
)

_college_opts = [
    "4-year college (standard track)",
    "Specialized 4-year college (art, music, film, etc.)",
    "Community college",
    "4-year college with an embedded IDD program (e.g., Adelphi Bridges, Mercyhurst AIM)",
    "Dedicated college for LD/IDD students (e.g., Landmark, Beacon, Mitchell)",
    "Non-degree college program for students with IDD (life skills + employability)",
]
_work_opts = [
    "Internship or work experience",
    "A job (competitive employment)",
    "Supported employment (a job with a coach)",
    "Vocational rehab / job training",
]
_programs_opts = [
    "18–21 transition program",
    "Day program",
    "Community / life-skills program",
]
_living_opts = [
    "Living independently",
    "Supported or group living",
    "Residential postsecondary program (e.g., Threshold, Riverview, College Internship Program)",
    "Staying home for now",
]
_other_opts = [
    "Gap year program",
    "Undecided / not sure",
    "Something else",
]

st.markdown("**College & college-based programs**")
sel_college = checkbox_group(_college_opts, _picked(_college_opts, "considering"), "head_col")
st.markdown("**Work & employment**")
sel_work = checkbox_group(_work_opts, _picked(_work_opts, "considering"), "head_work")
st.markdown("**Programs & day services**")
sel_programs = checkbox_group(_programs_opts, _picked(_programs_opts, "considering"), "head_prog")
st.markdown("**Living arrangements**")
sel_living = checkbox_group(_living_opts, _picked(_living_opts, "considering"), "head_live")
st.markdown("**Still figuring it out**")
sel_other = checkbox_group(_other_opts, _picked(_other_opts, "considering"), "head_other")

considering = sel_college + sel_work + sel_programs + sel_living + sel_other

considering_other = ""
if "Something else" in considering:
    considering_other = st.text_input(
        "What else are they considering?",
        value=_txt("considering_other"),
        key="considering_other",
    )

# Conditional follow-ups
_four_year = [
    "4-year college (standard track)",
    "Specialized 4-year college (art, music, film, etc.)",
]
college_idd_program = ""
if any(c in considering for c in _four_year):
    _idd_prog_opts = ["Yes", "Standard accommodations only", "Don't know", "Haven't chosen a school yet"]
    college_idd_program = st.radio(
        "Does the college offer a specialized program for students with IDD?",
        options=_idd_prog_opts,
        index=_idx(_idd_prog_opts, "college_idd_program"),
        key="college_idd_program",
    )

community_college_time = ""
if "Community college" in considering:
    _cc_opts = ["Full time", "Part time", "Not sure yet"]
    community_college_time = st.radio(
        "Community college — enrollment status?",
        options=_cc_opts,
        index=_idx(_cc_opts, "community_college_time"),
        key="community_college_time",
    )

transition_program_type = ""
if "18–21 transition program" in considering:
    _tp_opts = ["Public school district", "Private paid program", "Not sure"]
    transition_program_type = st.radio(
        "The 18–21 transition program — public school district or private paid?",
        options=_tp_opts,
        index=_idx(_tp_opts, "transition_program_type"),
        key="transition_program_type",
    )

college_location = ""
if any(c in considering for c in _college_opts):
    _loc_opts = ["In state", "Out of state", "Could be either", "Haven't chosen yet"]
    college_location = st.radio(
        "If they have a school in mind, is it in state or out of state?",
        options=_loc_opts,
        index=_idx(_loc_opts, "college_location"),
        key="college_location",
    )

st.write("---")

# ─────────────────────────────────────────────
# Section 7: What's on your mind
# ─────────────────────────────────────────────
st.header("What's on your mind")

q(
    "Q18. What's coming up in the next six months that you're worried about?",
    "A graduation, an 18th birthday, an IEP meeting, a letter you got, a deadline you can't quite remember.",
)
next_six_months = st.text_area(
    "Q18", value=_txt("next_six_months"), label_visibility="collapsed", height=140
)

q("Q19. What's keeping you up at night about this whole transition?", "Be honest. We're not going anywhere.")
keeping_up_at_night = st.text_area(
    "Q19", value=_txt("keeping_up_at_night"), label_visibility="collapsed", height=140
)

q(
    "Q20. What's on your to-do list right now?",
    "Whatever's already on your mental list — calls you keep meaning to make, forms you've been "
    "avoiding, conversations you need to have.",
)
todo_list = st.text_area("Q20", value=_txt("todo_list"), label_visibility="collapsed", height=120)

st.write("")
submitted = st.button("Save and continue", type="primary")

# ─────────────────────────────────────────────
# Handle submit
# ─────────────────────────────────────────────
if submitted:
    profile_payload = {
        "intake_version": "0.4",
        "your_name": your_name,
        "relationship": relationship,
        "relationship_other": relationship_other,
        "their_name": their_name,
        "their_age": their_age,
        "diagnoses": diagnoses,
        "diagnoses_other": diagnoses_other,
        "communication": communication,
        "associated_challenges": associated_challenges,
        "challenges_everyday": challenges_everyday,
        "strategies_worked": strategies_worked,
        "strategies_not_worked": strategies_not_worked,
        "strengths": strengths,
        "where_they_shine": where_they_shine,
        "anything_else": anything_else,
        "state": state,
        "nj_county": nj_county,
        "ny_region": ny_region,
        "other_state": other_state,
        "support_network": support_network,
        "education_status": education_status,
        "hs_type": hs_type,
        "hs_year": hs_year,
        "hs_plan": hs_plan,
        "postsec_stage": postsec_stage,
        "education_other": education_other,
        "grad_date": grad_date,
        "transition_pieces": transition_pieces,
        "transition_context": transition_context,
        "legal_stack": legal_stack,
        "legal_route": legal_route,
        "transition_catch_all": transition_catch_all,
        "insurance": insurance,
        "worked_with_past": worked_with_past,
        "worked_with_current": worked_with_current,
        "worked_with_other": worked_with_other,
        "current_program": current_program,
        "considering": considering,
        "considering_other": considering_other,
        "college_idd_program": college_idd_program,
        "community_college_time": community_college_time,
        "transition_program_type": transition_program_type,
        "college_location": college_location,
        "next_six_months": next_six_months,
        "keeping_up_at_night": keeping_up_at_night,
        "todo_list": todo_list,
    }
    if _p.get("parent_note"):
        profile_payload["parent_note"] = _p["parent_note"]
    st.session_state["profile"] = profile_payload
    st.session_state.pop("confirmed", None)
    save_profile(profile_payload)
    st.success(f"Got it{', ' + your_name if your_name else ''}. Your answers are saved for this session.")

# Post-save actions live OUTSIDE the submit block, gated on the saved profile.
# (Clicking the download button triggers a rerun where `submitted` is False, so
# anything gated on `submitted` would vanish. Gating on the saved profile keeps
# the download + continue link on screen.)
if st.session_state.get("profile"):
    st.download_button(
        "Download a copy of your answers",
        data=build_export_text(st.session_state["profile"]),
        file_name="the-route-my-answers.txt",
        mime="text/plain",
        help="Keep this as a backup. If a later screen ever looks empty, you can email this file to mkunken@gmail.com.",
    )
    st.page_link("pages/2_Review.py", label="Check what we understood →")
