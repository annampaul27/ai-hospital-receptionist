from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.chat import router as chat_router
from app.routers.webhook import router as webhook_router
from app.logger import logger

app = FastAPI(
    title='AI Hospital Receptionist',
    description='A conversational hospital receptionist backend using FastAPI, Supabase, and LangGraph.',
    version='1.0.0',
)

# Allow frontend hosts to access the API. In hosted deployments, set this to the frontend URL
# or use ['*'] if the host origin is dynamic. Replace with a tighter policy for production.
origins = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    '*',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(chat_router)
app.include_router(webhook_router)

@app.get('/')
def health_check() -> dict:
    logger.info('Health check requested')
    return {'status': 'ok', 'message': 'Hospital receptionist backend is running.'}
