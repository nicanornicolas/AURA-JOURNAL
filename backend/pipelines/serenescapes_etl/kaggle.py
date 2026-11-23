"""Run the pipeline inside a Kaggle notebook.

In a Kaggle cell:
    !git clone --depth 1 -b <branch> https://github.com/nicanornicolas/AURA-JOURNAL.git
    %cd AURA-JOURNAL/backend
    !pip install -q pydantic-settings loguru pyairtable httpx sqlalchemy
    from pipelines.serenescapes_etl.kaggle import run_on_kaggle
    run_on_kaggle("all")            # or "extract", "annotate", "load"

Add secrets under Add-ons > Secrets (only the ones you use):
FOURSQUARE_API_KEY, GEMINI_API_KEY, AIRTABLE_PAT, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, ANNOTATOR
"""

import os

SECRETS = ["FOURSQUARE_API_KEY", "GEMINI_API_KEY", "AIRTABLE_PAT", "AIRTABLE_BASE_ID",
           "AIRTABLE_TABLE_NAME", "ANNOTATOR", "DATABASE_URL"]


def load_kaggle_secrets() -> list[str]:
    from kaggle_secrets import UserSecretsClient  # only exists on Kaggle

    client, found = UserSecretsClient(), []
    for name in SECRETS:
        try:
            os.environ[name] = client.get_secret(name)
            found.append(name)
        except Exception:
            pass
    os.environ.setdefault("DATA_DIR", "/kaggle/working/serenescapes")
    return found


def run_on_kaggle(stage: str = "all") -> None:
    from .run import main

    print("Loaded secrets:", load_kaggle_secrets())
    main([stage])
