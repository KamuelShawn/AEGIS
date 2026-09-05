from fastapi import APIRouter

from app.providers.registry import registry

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status")
def get_status():
    return registry.status_report()
