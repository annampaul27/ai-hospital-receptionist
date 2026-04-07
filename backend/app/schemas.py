from pydantic import BaseModel, Field, validator
from typing import Any, Dict, List, Optional
from datetime import datetime

class ConversationMessage(BaseModel):
    role: str
    text: str

class SessionState(BaseModel):
    user_message: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[str] = None
    patient_query: Optional[str] = None
    ward: Optional[str] = None
    next_prompt: Optional[str] = None
    completed: bool = False
    webhook_sent: bool = False
    error: Optional[str] = None
    completion_timestamp: Optional[str] = None
    history: List[ConversationMessage] = Field(default_factory=list)
    assistant_message: Optional[str] = None

class ChatRequest(BaseModel):
    user_message: str
    session_state: Optional[SessionState] = None

    @validator('user_message')
    def validate_user_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('User message must not be empty')
        return value.strip()

class PatientSummary(BaseModel):
    patient_name: str
    patient_age: str
    patient_query: str
    ward: str
    timestamp: str

class ChatResponse(BaseModel):
    assistant_message: str
    session_state: SessionState
    patient_summary: Optional[PatientSummary] = None
    error: Optional[str] = None

class WebhookRequest(BaseModel):
    patient_name: str
    patient_age: str
    patient_query: str
    ward: str
    timestamp: Optional[str] = None

    @validator('patient_name')
    def name_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('Patient name is required')
        return value.strip()

    @validator('patient_age')
    def age_must_be_numeric(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError('Patient age must be numeric')
        return value

    @validator('patient_query')
    def query_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('Patient query is required')
        return value.strip()

    @validator('ward')
    def ward_must_be_valid(cls, value: str) -> str:
        valid_wards = {
            'General Ward', 'Emergency Ward', 'Mental Health Ward', 
            'Cardiology Ward', 'Orthopedics Ward', 'Pediatrics Ward'
        }
        if value not in valid_wards:
            raise ValueError(f'Ward must be one of {valid_wards}')
        return value

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        payload = super().dict(*args, **kwargs)
        if payload.get('timestamp') is None:
            payload['timestamp'] = datetime.utcnow().isoformat()
        return payload
