from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.get("/healthz", response_class=PlainTextResponse)
async def health_check():
    return "ok"
