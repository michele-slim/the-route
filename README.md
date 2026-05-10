# The Route

AI guide for parents and caregivers of young people (16–26) with IDD navigating the transition to adulthood.

Built for the ACL Caregiver AI Prize Challenge (deadline July 31, 2026).

## Stack

- Streamlit (web UI)
- Anthropic Claude API (the brain)
- Local JSON for V1 profile storage

## Run locally

```bash
source venv/bin/activate
streamlit run app.py
```

Browser opens automatically at http://localhost:8501

## Project layout

```
the-route-app/
├── app.py                  Entry point + welcome page
├── pages/                  Multi-page Streamlit pages
│   ├── 1_Intake.py         10-min questionnaire
│   ├── 2_Snapshot.py       Personalized "where you are"
│   ├── 3_Next_Steps.py     Prioritized actions
│   └── 4_Chat.py           Conversation with Claude
├── lib/                    Shared logic
│   ├── claude_client.py    Anthropic API wrapper
│   ├── profile.py          User profile model + save/load
│   ├── kb_loader.py        Loads KB markdown into context
│   └── prompts.py          System prompts for each page
├── data/
│   ├── kb/                 Knowledge base (~30 markdown files)
│   └── profiles/           Per-user profile JSON (gitignored)
├── .streamlit/
│   └── secrets.toml        API key (gitignored)
├── requirements.txt
└── .gitignore
```

## Setup

1. Create venv: `python3 -m venv venv`
2. Activate: `source venv/bin/activate`
3. Install: `pip install -r requirements.txt`
4. Add API key to `.streamlit/secrets.toml`
5. Run: `streamlit run app.py`
