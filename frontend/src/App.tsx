import { FormEvent, useEffect, useMemo, useRef, useState } from 'react'
import { Message, SessionState } from './types'
import { sendChatMessage } from './services/api'
import ChatBubble from './components/ChatBubble'
import PatientSummary from './components/PatientSummary'

const INITIAL_PROMPT = 'Hello! I am your hospital receptionist assistant. Please type your first message to begin.'

function generateId() {
  return Math.random().toString(36).substring(2, 10)
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    { id: generateId(), role: 'assistant', text: INITIAL_PROMPT },
  ])
  const [sessionState, setSessionState] = useState<SessionState>({})
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [summary, setSummary] = useState<SessionState | null>(null)
  const chatEndRef = useRef<HTMLDivElement | null>(null)

  const lastMessage = useMemo(() => messages[messages.length - 1], [messages])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmed = input.trim()
    if (!trimmed) {
      return
    }

    const userMsg: Message = { id: generateId(), role: 'user', text: trimmed }
    const updatedMessages = [...messages, userMsg]
    setMessages(updatedMessages)
    setInput('')
    setError('')
    setLoading(true)

    try {
      const response = await sendChatMessage(trimmed, sessionState)
      const assistantMsg: Message = {
        id: generateId(),
        role: 'assistant',
        text: response.assistant_message,
      }
      setMessages(prev => [...prev, assistantMsg])
      setSessionState(response.session_state)
      if (response.patient_summary) {
        setSummary(response.session_state)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred.')
      setMessages(prev => [
        ...prev,
        { id: generateId(), role: 'assistant', text: 'Sorry, something went wrong while processing your request.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl">
        <header className="mb-8 rounded-[2rem] border border-slate-200 bg-white/90 p-8 shadow-chat backdrop-blur-md">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-semibold text-slate-900">AI Hospital Receptionist</h1>
              <p className="mt-2 max-w-2xl text-slate-600">
                Chat naturally and receive ward classification, patient registration, and secure routing.
              </p>
            </div>
            <div className="rounded-3xl bg-slate-100 px-4 py-3 text-sm text-slate-700 shadow-sm">
              Built with React, Tailwind, FastAPI, Supabase, and LangGraph.
            </div>
          </div>
        </header>

        <main className="grid gap-8 lg:grid-cols-[1.4fr_0.8fr]">
          <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-chat">
            <div className="mb-4 flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">Reception Chat</h2>
                <p className="text-sm text-slate-500">One question at a time. Share your name, age, and symptoms.</p>
              </div>
              <div className="rounded-full bg-sky-50 px-3 py-1 text-sm font-medium text-sky-700">
                {loading ? 'Typing...' : lastMessage.role === 'assistant' ? 'Assistant ready' : 'Waiting for input'}
              </div>
            </div>

            <div className="flex min-h-[420px] flex-col gap-4 overflow-hidden rounded-[1.75rem] border border-slate-200 bg-slate-50 p-5">
              <div className="flex-1 space-y-4 overflow-y-auto pr-2">
                {messages.map(message => (
                  <ChatBubble key={message.id} message={message} />
                ))}
                <div ref={chatEndRef} />
              </div>
            </div>

            <form className="mt-6 flex flex-col gap-3 sm:flex-row" onSubmit={handleSubmit}>
              <label className="sr-only" htmlFor="chat-input">
                Enter message
              </label>
              <input
                id="chat-input"
                value={input}
                onChange={event => setInput(event.target.value)}
                className="min-w-0 flex-1 rounded-3xl border border-slate-300 bg-white px-4 py-3 text-base text-slate-900 shadow-inner outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-200"
                placeholder="Type your message here..."
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center justify-center rounded-3xl bg-sky-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                {loading ? 'Sending...' : 'Send'}
              </button>
            </form>
            {error ? <p className="mt-3 text-sm text-rose-600">{error}</p> : null}
          </section>

          <aside className="space-y-6">
            <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-chat">
              <h3 className="text-lg font-semibold text-slate-900">How it works</h3>
              <ul className="mt-4 space-y-3 text-sm text-slate-600">
                <li>• Ask a single question at a time and maintain conversational flow.</li>
                <li>• Validate name and age before registering the patient.</li>
                <li>• Use AI-enhanced ward classification with emergency and mental health detection.</li>
                <li>• Persist patients securely in Supabase and trigger a relay webhook on completion.</li>
              </ul>
            </div>

            {summary ? (
              <PatientSummary
                name={summary.patient_name || ''}
                age={summary.patient_age || ''}
                query={summary.patient_query || ''}
                ward={summary.ward || ''}
                timestamp={summary.completion_timestamp || new Date().toISOString()}
              />
            ) : (
              <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-chat">
                <h3 className="text-lg font-semibold text-slate-900">Patient summary</h3>
                <p className="mt-3 text-sm text-slate-500">Complete registration to see the patient summary and classification badge.</p>
              </div>
            )}
          </aside>
        </main>
      </div>
    </div>
  )
}
