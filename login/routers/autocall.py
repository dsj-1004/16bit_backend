from fastapi import APIRouter, Depends, HTTPException

from login import schemas
from login.security import get_current_user

router = APIRouter(tags=["autocall"])


@router.post("/auto-call/trigger")
async def auto_call_trigger(
    payload: schemas.AutoCallTriggerRequest, user=Depends(get_current_user)
):
    # 최소 조건: 병원 목록이 비어있지 않아야 함
    if not payload.hospital_ids:
        return {"triggered": False}
    return {"triggered": True}
