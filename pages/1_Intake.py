"""
Intake page — The Route
v0.2 questionnaire (May 10, 2026 — with Nora).

Saves to st.session_state["profile"] on submit.
JSON persistence comes later.
"""

import streamlit as st

from lib.profile import save_profile, hydrate_session_state

st.set_page_config(page_title="Intake — The Route", layout="centered")
hydrate_session_state()

# ─────────────────────────────────────────────
# Welcome / what to expect
# ─────────────────────────────────────────────
st.title("Tell us about your young person.")
st.write(
    "This takes about **10 to 15 minutes**. Everything stays on your computer. "
    "You can save and come back if you need to step away."
)
st.write("---")

with st.form("intake_form"):

    # ─────────────────────────────────────────────
    # Section 1: About you
    # ─────────────────────────────────────────────
    st.header("About you")

    your_name = st.text_input(
        "What's your first name?",
        help="This will only be used when it makes sense. Stays on your computer.",
    )

    relationship = st.selectbox(
        "Who are you to them?",
        options=[
            "Parent",
            "Grandparent",
            "Sibling",
            "Foster or kinship caregiver",
            "Aunt / uncle",
            "Other",
        ],
    )
    relationship_other = st.text_input(
        "If other, please specify:",
        key="relationship_other",
    )

    st.write("")

    # ─────────────────────────────────────────────
    # Section 2: Describe your teen / young adult
    # ─────────────────────────────────────────────
    st.header("Describe your teen / young adult")

    their_name = st.text_input("What's their first name?")

    their_age = st.selectbox(
        "How old are they?",
        options=list(range(16, 27)),
    )

    diagnoses = st.multiselect(
        "Have they been diagnosed with a disability? Check all that apply.",
        options=[
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
        ],
    )
    diagnoses_other = st.text_input(
        "If something else, tell me more:",
        key="diagnoses_other",
    )

    primary_challenges = st.text_area(
        "What are the primary challenges? (e.g. executive functioning, mood regulation, social / pragmatic speech issues)",
        help="Please be as comprehensive as possible.",
        height=120,
    )

    primary_strengths = st.text_area(
        "What are their primary strengths? (e.g. working memory, visual processing skills, inferential reasoning)",
        height=120,
    )

    communication = st.radio(
        "How do they communicate, mostly?",
        options=[
            "Speaks fluently",
            "Speaks, but with limits or support",
            "Uses AAC, sign, or another tool",
            "Nonverbal",
        ],
    )

    what_they_love = st.text_area(
        "Tell us a little more about them. What do they love? (e.g. reading, music, pro-wrestling, traveling, video games — tell us everything.)",
        height=120,
    )

    what_they_hate = st.text_area(
        "What do they hate? (e.g. certain foods, crowds, homework, medical appointments)",
        height=120,
    )

    what_great_at = st.text_area(
        "What are they great at? (e.g. basketball, drawing, math, playing drums)",
        help="Not a clinical question. It's about who they are, not what they have.",
        height=120,
    )

    where_they_struggle = st.text_area(
        "Where do they struggle? (e.g. socializing, rule following, independent living skills)",
        height=120,
    )

    typical_day = st.text_area(
        "What's a typical day like? The good parts and the hard parts.",
        help="Whatever you'd tell a friend. Don't polish it.",
        height=140,
    )

    st.write("")

    # ─────────────────────────────────────────────
    # Section 3: Where you live
    # ─────────────────────────────────────────────
    st.header("Where you live")

    state = st.selectbox(
        "What state are you in?",
        options=["New Jersey", "New York", "Other"],
    )
    nj_county = st.text_input("If NJ, what county?", key="nj_county")
    ny_region = st.selectbox(
        "If NY, what region?",
        options=[
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
        ],
        key="ny_region",
    )
    other_state = st.text_input("If other, which state?", key="other_state")

    st.write("")

    # ─────────────────────────────────────────────
    # Section 4: Where they are right now
    # ─────────────────────────────────────────────
    st.header("Where they are right now")

    school_status = st.radio(
        "School-wise, where are they?",
        options=[
            "Still in high school (with an IEP)",
            "In an 18–21 transition program",
            "In college or a postsecondary program",
            "Recently aged out, nothing in place yet",
            "Something else / not sure",
        ],
    )

    col1, col2 = st.columns(2)
    with col1:
        grad_month = st.selectbox(
            "If still in high school, expected graduation month",
            options=[
                "—",
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
                "Not sure",
            ],
        )
    with col2:
        grad_year = st.selectbox(
            "Year",
            options=["—", "2026", "2027", "2028", "2029", "2030", "2031", "Not sure"],
        )

    whats_next = st.text_area(
        "What's next? What does your teen / young adult want to do next? (e.g. college, gap year, residential living)",
        height=120,
    )

    good_options = st.text_area(
        "What options seem like a good idea to you? (e.g. supported living, community college, four-year institution)",
        height=120,
    )

    st.write("**Of these big transition pieces, which are done, which haven't started, which are you not sure about?**")
    transition_pieces = {}
    for label in [
        "Registered with the state's developmental disability agency (DDD in NJ, OPWDD in NY)",
        "Applied for SSI",
        "Guardianship or supported decision-making decision",
        "Connected to vocational rehab (DVRS in NJ, ACCES-VR in NY)",
        "Medicaid waiver applied for",
        "A plan for what comes after school",
    ]:
        transition_pieces[label] = st.radio(
            label,
            options=["Done", "Not started", "Unnecessary", "Not sure"],
            horizontal=True,
            key=f"piece::{label}",
        )

    insurance = st.radio(
        "What's their health insurance situation?",
        options=[
            "On a parent's private plan",
            "On Medicaid",
            "Both",
            "Not sure",
        ],
    )

    st.write("")

    # ─────────────────────────────────────────────
    # Section 5: Who's around you
    # ─────────────────────────────────────────────
    st.header("Who's around you")

    support_network = st.multiselect(
        "Who else is in the picture day-to-day?",
        options=[
            "Co-parent / other parent in the home",
            "Other parent (separated or co-parenting)",
            "Siblings (any age)",
            "Grandparents",
            "Paid support staff or aides",
            "Extended family",
            "It's mostly just me",
            "Other",
        ],
    )

    professionals = st.multiselect(
        "Have you worked with any of these?",
        options=[
            "A parent advocate",
            "A special-ed attorney",
            "A transition coordinator at the school",
            "A service coordinator (NJ DDD or NY OPWDD)",
            "A parent center (SPAN, Arc, etc.)",
            "A private case manager or planner",
            "None of the above",
        ],
    )

    st.write("")

    # ─────────────────────────────────────────────
    # Section 6: What's on your mind
    # ─────────────────────────────────────────────
    st.header("What's on your mind")

    next_six_months = st.text_area(
        "What's coming up in the next six months that you're worried about?",
        help="A graduation, an 18th birthday, an IEP meeting, a letter you got, a deadline you can't quite remember.",
        height=140,
    )

    keeping_up_at_night = st.text_area(
        "What's keeping you up at night about this whole transition?",
        help="Be honest. The more real this is, the more useful it is.",
        height=140,
    )

    st.write("")
    submitted = st.form_submit_button("Save and continue")

# ─────────────────────────────────────────────
# Handle submit
# ─────────────────────────────────────────────
if submitted:
    profile_payload = {
        "your_name": your_name,
        "relationship": relationship,
        "relationship_other": relationship_other,
        "their_name": their_name,
        "their_age": their_age,
        "diagnoses": diagnoses,
        "diagnoses_other": diagnoses_other,
        "primary_challenges": primary_challenges,
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
        "transition_pieces": transition_pieces,
        "insurance": insurance,
        "support_network": support_network,
        "professionals": professionals,
        "next_six_months": next_six_months,
        "keeping_up_at_night": keeping_up_at_night,
    }
    st.session_state["profile"] = profile_payload
    save_profile(profile_payload)
    st.success(f"Got it{', ' + your_name if your_name else ''}. Profile saved.")
    st.page_link("pages/2_Snapshot.py", label="See your Snapshot →")
    with st.expander("What we captured"):
        st.json(profile_payload)
