"""
Intake page — The Route
v0.3 questionnaire (May 29, 2026 spec — built June 11).

Changes from v0.2 per the Intake v0.3 doc:
- Q6 wording fix + Q6a/Q6b best day / worst day
- Q15 school status splits college into entering vs. continuing
- Q19 structured post-school path question + adaptive follow-ups
- Q20 matrix: Accepted/Pending/Rejected/Not started/Not sure,
  guardianship as a multi-check, adaptive follow-ups, catch-all
- Q21 insurance adds "No insurance"
- Section 4b: what you've tried so far
- Q23 split: have worked with vs. currently work with
- Q26: what's on your to-do list

No st.form — adaptive follow-ups need live reruns. Widgets hold their
own state via keys; the save button at the bottom assembles the profile.
Pre-fills from the saved profile so "Edit something" returns the parent
to their answers.
"""

import streamlit as st

from lib.profile import save_profile, hydrate_session_state

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


# ─────────────────────────────────────────────
# Welcome / what to expect
# ─────────────────────────────────────────────
st.title("Tell us about your young person.")
st.write(
    "This takes about **10 to 15 minutes**. Everything stays on your computer. "
    "You can save and come back if you need to step away."
)
if _p:
    st.info("Your earlier answers are filled in below. Change whatever needs changing and save again.")
st.write("---")

# ─────────────────────────────────────────────
# Section 1: About you
# ─────────────────────────────────────────────
st.header("About you")

your_name = st.text_input(
    "What's your first name?",
    value=_txt("your_name"),
    help="We'll use it when it makes sense. This all stays on your computer.",
)

_relationship_opts = [
    "Parent",
    "Grandparent",
    "Sibling",
    "Foster or kinship caregiver",
    "Aunt / uncle",
    "Other",
]
relationship = st.selectbox(
    "Who are you to them?",
    options=_relationship_opts,
    index=_idx(_relationship_opts, "relationship"),
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
# Section 2: Describe your teen / young adult
# ─────────────────────────────────────────────
st.header("Describe your teen / young adult")

their_name = st.text_input("What's their first name?", value=_txt("their_name"))

_age_opts = list(range(16, 27))
their_age = st.selectbox(
    "How old are they?",
    options=_age_opts,
    index=_age_opts.index(_p["their_age"]) if _p.get("their_age") in _age_opts else 0,
)

_diagnosis_opts = [
    "ADHD",
    "Anxiety",
    "Autism",
    "Bipolar Disorder",
    "Central Auditory Processing Disorder (CAPD)",
    "Cerebral Palsy",
    "Complex or multiple disabilities",
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
    "Prefer not to say",
]
diagnoses = st.multiselect(
    "Have they been diagnosed with a disability? Check all that apply.",
    options=_diagnosis_opts,
    default=_picked(_diagnosis_opts, "diagnoses"),
)
diagnoses_other = ""
if "Something Else" in diagnoses:
    diagnoses_other = st.text_input(
        "Tell us more about the diagnosis:",
        value=_txt("diagnoses_other"),
        key="diagnoses_other",
    )

primary_challenges = st.text_area(
    "What are *their* primary challenges? (e.g. executive functioning, mood regulation, social / pragmatic speech issues)",
    value=_txt("primary_challenges"),
    help="Please be as comprehensive as possible.",
    height=120,
)

best_day_challenges = st.text_area(
    "What are their behavioral challenges on their best day?",
    value=_txt("best_day_challenges"),
    height=100,
)

worst_day_challenges = st.text_area(
    "What are their behavioral challenges on their worst day?",
    value=_txt("worst_day_challenges"),
    height=100,
)

primary_strengths = st.text_area(
    "What are their primary strengths? (e.g. working memory, visual processing skills, inferential reasoning)",
    value=_txt("primary_strengths"),
    height=120,
)

_communication_opts = [
    "Speaks fluently",
    "Speaks, but with limits or support",
    "Uses AAC, sign, or another tool",
    "Nonverbal",
]
communication = st.radio(
    "How do they communicate, mostly?",
    options=_communication_opts,
    index=_idx(_communication_opts, "communication"),
)

what_they_love = st.text_area(
    "Tell us a little more about them. What do they love? (e.g. reading, music, pro-wrestling, traveling, video games — tell us everything.)",
    value=_txt("what_they_love"),
    height=120,
)

what_they_hate = st.text_area(
    "What do they hate? (e.g. certain foods, crowds, homework, medical appointments)",
    value=_txt("what_they_hate"),
    height=120,
)

what_great_at = st.text_area(
    "What are they great at? (e.g. basketball, drawing, math, playing drums)",
    value=_txt("what_great_at"),
    help="This isn't a clinical question. We want to actually know them.",
    height=120,
)

where_they_struggle = st.text_area(
    "Where do they struggle? (e.g. socializing, rule following, independent living skills)",
    value=_txt("where_they_struggle"),
    height=120,
)

typical_day = st.text_area(
    "What's a typical day like? The good parts and the hard parts.",
    value=_txt("typical_day"),
    help="Whatever you'd tell a friend. Don't polish it.",
    height=140,
)

st.write("---")

# ─────────────────────────────────────────────
# Section 3: Where you live
# ─────────────────────────────────────────────
st.header("Where you live")

_state_opts = ["New Jersey", "New York", "Other"]
state = st.selectbox(
    "What state are you in?",
    options=_state_opts,
    index=_idx(_state_opts, "state"),
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
# Section 4: Where they are right now
# ─────────────────────────────────────────────
st.header("Where they are right now")

_school_opts = [
    "Still in high school (with an IEP)",
    "In an 18–21 transition program",
    "In college or a postsecondary program (entering this fall)",
    "In college or a postsecondary program (continuing)",
    "Recently aged out, nothing in place yet",
    "Something else / not sure",
]
school_status = st.radio(
    "School-wise, where are they?",
    options=_school_opts,
    index=_idx(_school_opts, "school_status"),
)

grad_month = "—"
grad_year = "—"
if school_status in ("Still in high school (with an IEP)", "In an 18–21 transition program"):
    _month_opts = [
        "—",
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        "Not sure",
    ]
    _year_opts = ["—", "2026", "2027", "2028", "2029", "2030", "2031", "Not sure"]
    col1, col2 = st.columns(2)
    with col1:
        grad_month = st.selectbox(
            "When are they expected to graduate or age out? Month:",
            options=_month_opts,
            index=_idx(_month_opts, "grad_month"),
        )
    with col2:
        grad_year = st.selectbox(
            "Year:",
            options=_year_opts,
            index=_idx(_year_opts, "grad_year"),
        )

whats_next = st.text_area(
    "What does your young person want to do next?",
    value=_txt("whats_next"),
    height=120,
)

good_options = st.text_area(
    "What options seem like a good idea to you?",
    value=_txt("good_options"),
    height=120,
)

st.write("**Which of these are they considering? Check all that apply.**")

_college_opts = [
    "4-year college, standard track",
    "Specialized 4-year college — art school, music conservatory, film school, etc.",
    "4-year college that also has a specialized IDD program inside it (Adelphi Bridges, Mercyhurst AIM)",
    "Dedicated college built for LD/IDD students (Landmark, Beacon, Mitchell)",
    "Community college",
    "Stand-alone college program for students with IDD — not a full degree, focused on life skills + employability",
]
_noncollege_opts = [
    "Residential post-secondary IDD program (Threshold, Riverview, College Internship Program)",
    "18–21 transition program",
    "Gap year program",
    "Vocational rehab → work",
    "Day program",
    "Stay home, no formal placement",
    "Undecided / not sure",
    "Something else",
]
considering_college = st.multiselect(
    "College / college-based:",
    options=_college_opts,
    default=_picked(_college_opts, "considering"),
)
considering_noncollege = st.multiselect(
    "Non-college:",
    options=_noncollege_opts,
    default=_picked(_noncollege_opts, "considering"),
)
considering = considering_college + considering_noncollege

considering_other = ""
if "Something else" in considering:
    considering_other = st.text_input(
        "What else are they considering?",
        value=_txt("considering_other"),
        key="considering_other",
    )

# Q19 adaptive follow-ups
college_idd_program = ""
if (
    "4-year college, standard track" in considering
    or "Specialized 4-year college — art school, music conservatory, film school, etc." in considering
):
    _idd_prog_opts = [
        "Yes",
        "Standard accommodations only",
        "Don't know",
        "Haven't picked the school yet",
    ]
    college_idd_program = st.radio(
        "Does the college offer a specialized program for students with IDD (e.g., Adelphi Bridges, Mercyhurst AIM)?",
        options=_idd_prog_opts,
        index=_idx(_idd_prog_opts, "college_idd_program"),
        key="college_idd_program",
    )

community_college_time = ""
if "Community college" in considering:
    _cc_opts = ["Full time", "Part time", "Not sure yet"]
    community_college_time = st.radio(
        "Community college — full time or part time?",
        options=_cc_opts,
        index=_idx(_cc_opts, "community_college_time"),
        key="community_college_time",
    )

transition_program_type = ""
if "18–21 transition program" in considering:
    _tp_opts = ["Public school-district program", "Private paid program", "Not sure"]
    transition_program_type = st.radio(
        "The 18–21 transition program — public school-district or private paid?",
        options=_tp_opts,
        index=_idx(_tp_opts, "transition_program_type"),
        key="transition_program_type",
    )

college_location = ""
if any(c in considering for c in _college_opts):
    _loc_opts = ["In state", "Out of state", "Could be either", "Haven't picked yet"]
    college_location = st.radio(
        "If they have a school in mind, is it in state or out of state?",
        options=_loc_opts,
        index=_idx(_loc_opts, "college_location"),
        key="college_location",
    )

st.write("")
st.write("**Of these big transition pieces, where do things stand?**")

_piece_status_opts = ["Accepted", "Pending", "Rejected", "Not started", "Not sure"]
_piece_rows = [
    "Registered with the state's developmental disability agency (DDD in NJ, OPWDD in NY)",
    "Applied for SSI",
    "Connected to vocational rehab (DVRS in NJ, ACCES-VR in NY)",
    "Medicaid waiver applied for",
]
_saved_pieces = _p.get("transition_pieces") or {}
_saved_context = _p.get("transition_context") or {}
transition_pieces = {}
transition_context = {}
for label in _piece_rows:
    transition_pieces[label] = st.radio(
        label,
        options=_piece_status_opts,
        index=_piece_status_opts.index(_saved_pieces[label]) if _saved_pieces.get(label) in _piece_status_opts else 3,
        horizontal=True,
        key=f"piece::{label}",
    )
    # Adaptive follow-ups per the v0.3 spec
    if transition_pieces[label] == "Accepted":
        _drv_opts = ["Me", "My young person", "A counselor or coordinator"]
        saved = _saved_context.get(label)
        transition_context[label] = st.radio(
            "Who's driving it — you, your young person, or a counselor?",
            options=_drv_opts,
            index=_drv_opts.index(saved) if saved in _drv_opts else 0,
            horizontal=True,
            key=f"context::{label}",
        )
    elif transition_pieces[label] == "Not started":
        _why_opts = ["Ruled out", "Not relevant", "Not sure what it is"]
        saved = _saved_context.get(label)
        transition_context[label] = st.radio(
            "Ruled out, not relevant, or not sure what it is?",
            options=_why_opts,
            index=_why_opts.index(saved) if saved in _why_opts else 2,
            horizontal=True,
            key=f"context::{label}",
        )

st.write("**Guardianship / supported decision-making / legal paperwork — what's in place?**")
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
legal_stack = st.multiselect(
    "Check everything that applies.",
    options=_legal_opts,
    default=_picked(_legal_opts, "legal_stack"),
)
legal_route = ""
if any(item in legal_stack for item in _legal_opts[:6]):
    legal_route = st.text_input(
        "What route did you take? (e.g., Mama Bear forms, attorney, court)",
        value=_txt("legal_route"),
        key="legal_route",
    )

transition_catch_all = st.text_area(
    "Anything else worth flagging about the legal / benefits / services list?",
    value=_txt("transition_catch_all"),
    height=100,
)

_insurance_opts = [
    "On a parent's private plan",
    "On Medicaid",
    "Both",
    "No insurance",
    "Not sure",
]
insurance = st.radio(
    "What's their health insurance situation?",
    options=_insurance_opts,
    index=_idx(_insurance_opts, "insurance"),
)

st.write("---")

# ─────────────────────────────────────────────
# Section 4b: What you've tried so far
# ─────────────────────────────────────────────
st.header("What you've tried so far")
st.caption("Outside formal services.")

tried_working = st.text_area(
    "What have you tried that's working for them?",
    value=_txt("tried_working"),
    help="Social stuff, life skills, support strategies, anything you've experimented with outside formal programs.",
    height=120,
)

tried_not_working = st.text_area(
    "What have you tried that didn't fit or didn't work?",
    value=_txt("tried_not_working"),
    help="Honestly — improv class, a coach, a routine, a club, a system. Anything we shouldn't suggest again because you've already been there.",
    height=120,
)

st.write("---")

# ─────────────────────────────────────────────
# Section 5: Who's around you
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
support_network = st.multiselect(
    "Who else is in the picture day-to-day?",
    options=_support_opts,
    default=_picked(_support_opts, "support_network"),
)

_professional_opts = [
    "A parent advocate",
    "A special-ed attorney",
    "A transition coordinator at the school",
    "A service coordinator (NJ DDD or NY OPWDD)",
    "A parent center (SPAN, INCLUDEnyc, Arc, etc.)",
    "A private case manager or planner",
    "A therapist for the young person",
    "An EF / executive function coach",
    "None of the above",
]
col_past, col_current = st.columns(2)
with col_past:
    worked_with_past = st.multiselect(
        "Have worked with:",
        options=_professional_opts,
        default=_picked(_professional_opts, "worked_with_past"),
    )
with col_current:
    worked_with_current = st.multiselect(
        "Currently work with:",
        options=_professional_opts,
        default=_picked(_professional_opts, "worked_with_current"),
    )

st.write("---")

# ─────────────────────────────────────────────
# Section 6: What's on your mind
# ─────────────────────────────────────────────
st.header("What's on your mind")

next_six_months = st.text_area(
    "What's coming up in the next six months that you're worried about?",
    value=_txt("next_six_months"),
    help="A graduation, an 18th birthday, an IEP meeting, a letter you got, a deadline you can't quite remember.",
    height=140,
)

keeping_up_at_night = st.text_area(
    "What's keeping you up at night about this whole transition?",
    value=_txt("keeping_up_at_night"),
    help="Be honest. We're not going anywhere.",
    height=140,
)

todo_list = st.text_area(
    "What's on your to-do list right now?",
    value=_txt("todo_list"),
    help="Whatever's already on your mental list — calls you keep meaning to make, forms you've been avoiding, conversations you need to have.",
    height=120,
)

st.write("")
submitted = st.button("Save and continue", type="primary")

# ─────────────────────────────────────────────
# Handle submit
# ─────────────────────────────────────────────
if submitted:
    profile_payload = {
        "intake_version": "0.3",
        "your_name": your_name,
        "relationship": relationship,
        "relationship_other": relationship_other,
        "their_name": their_name,
        "their_age": their_age,
        "diagnoses": diagnoses,
        "diagnoses_other": diagnoses_other,
        "primary_challenges": primary_challenges,
        "best_day_challenges": best_day_challenges,
        "worst_day_challenges": worst_day_challenges,
        "primary_strengths": primary_strengths,
        "communication": communication,
        "what_they_love": what_they_love,
        "what_they_hate": what_they_hate,
        "what_great_at": what_great_at,
        "where_they_struggle": where_they_struggle,
        "typical_day": typical_day,
        "state": state,
        "nj_county": nj_county,
        "ny_region": ny_region,
        "other_state": other_state,
        "school_status": school_status,
        "grad_month": grad_month,
        "grad_year": grad_year,
        "whats_next": whats_next,
        "good_options": good_options,
        "considering": considering,
        "considering_other": considering_other,
        "college_idd_program": college_idd_program,
        "community_college_time": community_college_time,
        "transition_program_type": transition_program_type,
        "college_location": college_location,
        "transition_pieces": transition_pieces,
        "transition_context": transition_context,
        "legal_stack": legal_stack,
        "legal_route": legal_route,
        "transition_catch_all": transition_catch_all,
        "insurance": insurance,
        "tried_working": tried_working,
        "tried_not_working": tried_not_working,
        "support_network": support_network,
        "worked_with_past": worked_with_past,
        "worked_with_current": worked_with_current,
        "next_six_months": next_six_months,
        "keeping_up_at_night": keeping_up_at_night,
        "todo_list": todo_list,
    }
    # Carry forward any note the parent added on the review screen
    if _p.get("parent_note"):
        profile_payload["parent_note"] = _p["parent_note"]
    st.session_state["profile"] = profile_payload
    st.session_state.pop("confirmed", None)
    save_profile(profile_payload)
    st.success(f"Got it{', ' + your_name if your_name else ''}. Profile saved.")
    st.page_link("pages/2_Review.py", label="Check what we understood →")
    with st.expander("What we captured"):
        st.json(profile_payload)
