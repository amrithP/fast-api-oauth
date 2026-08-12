# Run from the fast-api-oauth/ folder:
#   .venv\Scripts\uvicorn auth_organized.main:app --reload

from fastapi import FastAPI

from auth_organized.routers.auth_router import router

app = FastAPI()

app.include_router(router)
