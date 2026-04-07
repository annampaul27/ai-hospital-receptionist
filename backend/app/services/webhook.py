import time
import httpx
from app.config import RELAY_APP_URL
from app.logger import logger

class WebhookService:
    def __init__(self, relay_url: str = RELAY_APP_URL) -> None:
        self.relay_url = relay_url

    def trigger_webhook(self, payload: dict) -> dict:
        logger.info('Triggering webhook to %s', self.relay_url)
        last_error = None
        for attempt in range(1, 4):
            try:
                with httpx.Client(timeout=10) as client:
                    response = client.post(self.relay_url, json=payload)
                if response.status_code in {200, 201, 202}:
                    logger.info('Webhook delivered successfully: %s', response.status_code)
                    return {'status': 'success', 'status_code': response.status_code}
                last_error = f'Unexpected status {response.status_code}: {response.text}'
                logger.warning('Webhook attempt %s failed: %s', attempt, last_error)
            except Exception as exc:
                last_error = str(exc)
                logger.warning('Webhook attempt %s exception: %s', attempt, last_error)
            time.sleep(attempt * 0.8)
        logger.error('Webhook failed after retries: %s', last_error)
        raise RuntimeError(f'Webhook failed after retries: {last_error}')
