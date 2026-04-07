from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from app.config import API_KEY
from app.logger import logger
from app.schemas import WebhookRequest
from app.services.webhook import WebhookService

router = APIRouter()

@router.post('/webhook')
async def webhook_endpoint(
    request: WebhookRequest,
    x_api_key: Optional[str] = Header(None),
) -> dict:
    if API_KEY and x_api_key != API_KEY:
        logger.warning('Unauthorized webhook request received')
        raise HTTPException(status_code=401, detail='Invalid API key')
    payload = request.dict()
    try:
        WebhookService().trigger_webhook(payload)
        return {'status': 'success', 'detail': 'Webhook sent successfully'}
    except Exception as exc:
        logger.exception('Webhook endpoint failed')
        raise HTTPException(status_code=500, detail=str(exc))
