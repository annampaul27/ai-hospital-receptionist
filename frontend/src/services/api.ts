import { ApiChatResponse, SessionState } from '../types'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
const API_KEY = import.meta.env.VITE_API_KEY || 'test-api-key-12345'

export async function sendChatMessage(userMessage: string, sessionState: SessionState) {
  const response = await fetch(`${BACKEND_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    },
    body: JSON.stringify({ user_message: userMessage, session_state: sessionState }),
  })

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => ({ detail: 'Unable to parse error' }))
    throw new Error(errorPayload.detail || 'Chat request failed')
  }

  return (await response.json()) as ApiChatResponse
}
