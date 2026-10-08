from collections import Counter

from fastapi import APIRouter

from scripts.data.registry import DatasetManager

router=APIRouter(prefix="/admin",tags=["admin"])
@router.get("/status")
def status():
    manager = DatasetManager()
    datasets = [manager.ensure(spec.name) for spec in manager.registry.list()]
    status_counts = Counter(dataset["status"] for dataset in datasets)
    return {
        "service": "api",
        "datasets": datasets,
        "datasets_by_status": dict(status_counts),
        "models": "fixture",
        "jobs": "demo",
    }
