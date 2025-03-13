from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from readme_metrics.VerifyWebhook import VerifyWebhook

from ..config import README_SECRET, README_ENABLED

router = APIRouter(prefix="/webhook", tags=["webhook"])



@router.post("", include_in_schema=False)
async def post_webhook(
    request: Request, data: Annotated[dict, Body()],
) -> str:
    if README_ENABLED:
        # Readme webhook
        signature = request.headers.get("readme-signature", None)
        
        try:
            VerifyWebhook(data, signature, README_SECRET)
        except Exception as error:
            raise HTTPException(status_code=403, detail=str(error))

    return "OK"