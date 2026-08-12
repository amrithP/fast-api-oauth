# Run once, from the fast-api-oauth/ folder:
#   .venv\Scripts\python -m auth_organized.scripts.create_tables

from auth_organized.db.database import Base, engine
from auth_organized import models  # noqa: F401  (import registers User/Role with Base)

Base.metadata.drop_all(bind=engine)  # drop first so re-running picks up model changes
Base.metadata.create_all(bind=engine)
