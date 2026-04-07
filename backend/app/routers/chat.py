from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from fastapi.concurrency import run_in_threadpool
from app.config import API_KEY
from app.logger import logger
from app.schemas import ChatRequest, ChatResponse, PatientSummary, SessionState
from app.services.langgraph_workflow import ReceptionWorkflow
from app.services.supabase_client import SupabaseClient
from app.services.webhook import WebhookService

router = APIRouter()

@router.post('/chat', response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    x_api_key: Optional[str] = Header(None),
) -> ChatResponse:
    if API_KEY and x_api_key != API_KEY:
        logger.warning('Unauthorized chat request received')
        raise HTTPException(status_code=401, detail='Invalid API key')

    session_state = request.session_state or SessionState()
    state_data = session_state.model_dump()
    state_data['user_message'] = request.user_message

    try:
        workflow = ReceptionWorkflow(SupabaseClient(), WebhookService())
        updated_state = await run_in_threadpool(workflow.run, state_data)
        session_state = SessionState.model_validate(updated_state)
        patient_summary = None
        if session_state.completed:
            patient_summary = PatientSummary(
                patient_name=session_state.patient_name or '',
                patient_age=session_state.patient_age or '',
                patient_query=session_state.patient_query or '',
                ward=session_state.ward or '',
                timestamp=session_state.completion_timestamp or '',
            )
        return ChatResponse(
            assistant_message=session_state.assistant_message or 'I am here to help you with hospital registration.',
            session_state=session_state,
            patient_summary=patient_summary,
        )
    except Exception as exc:
        logger.exception('Chat endpoint failed')
        raise HTTPException(status_code=500, detail=str(exc))
