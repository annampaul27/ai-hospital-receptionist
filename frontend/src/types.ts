export type Role = 'user' | 'assistant'

export interface Message {
  id: string
  role: Role
  text: string
}

export interface SessionState {
  user_message?: string
  patient_name?: string
  patient_age?: string
  patient_query?: string
  ward?: string
  next_prompt?: string
  completed?: boolean
  webhook_sent?: boolean
  completion_timestamp?: string
  history?: Message[]
}

export interface ApiChatResponse {
  assistant_message: string
  session_state: SessionState
  patient_summary?: {
    patient_name: string
    patient_age: string
    patient_query: string
    ward: string
    timestamp: string
  }
  error?: string
}
