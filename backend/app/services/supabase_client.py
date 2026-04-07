from datetime import datetime
from uuid import uuid4
import httpx
from app.config import SUPABASE_URL, SUPABASE_KEY
from app.logger import logger

class SupabaseClient:
    def __init__(self) -> None:
        self.base_url = SUPABASE_URL.rstrip('/')
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal',
        }

    def store_patient_record(self, patient_name: str, patient_age: str, patient_query: str, ward: str) -> dict:
        timestamp = datetime.utcnow().isoformat()
        record = {
            'id': str(uuid4()),
            'patient_name': patient_name,
            'patient_age': int(patient_age),
            'patient_query': patient_query,
            'ward': ward,
            'timestamp': timestamp,
            'created_at': timestamp,
        }
        logger.info('Saving patient record to Supabase for %s', patient_name)
        url = f'{self.base_url}/rest/v1/patients'

        response = httpx.post(url, headers=self.headers, json=[record], timeout=15.0)
        if response.status_code not in (200, 201, 204):
            logger.error('Supabase insert failed: %s %s', response.status_code, response.text)
            raise RuntimeError(f'Supabase insert failed: {response.status_code} {response.text}')

        return record
