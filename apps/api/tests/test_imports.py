from fastapi import FastAPI

from apps.api.app.main import app


def test_app_imports(): assert isinstance(app,FastAPI)
