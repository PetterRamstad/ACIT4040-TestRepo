from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.app.admin.router import router as admin_router
from apps.api.app.agent.router import router as agent_router
from apps.api.app.furniture.router import router as furniture_router
from apps.api.app.layouts.router import router as layout_router
from apps.api.app.preferences.router import router as preference_router
from apps.api.app.rooms.router import router as room_router

app=FastAPI(title="ACIT4040 Interior Design API",version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://[::1]:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health(): return {"status":"ok","service":"api"}

@app.get("/ready")
def ready(): return {"status":"ready","dependencies":{"database":"demo","vector_store":"fixture"}}

app.include_router(preference_router)
app.include_router(furniture_router)
app.include_router(room_router)
app.include_router(layout_router)
app.include_router(agent_router)
app.include_router(admin_router)
