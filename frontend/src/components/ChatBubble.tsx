import { Message } from '../types'

interface Props {
  message: Message
}

const bubbleStyling = {
  user: 'bg-sky-600 text-white self-end rounded-bl-2xl rounded-tl-2xl rounded-tr-2xl',
  assistant: 'bg-white text-slate-900 self-start rounded-br-2xl rounded-tl-2xl rounded-tr-2xl border border-slate-200',
}

export default function ChatBubble({ message }: Props) {
  return (
    <div className={`max-w-[85%] p-4 ${bubbleStyling[message.role]} shadow-sm`}>
      <div className="text-sm font-medium mb-2 text-slate-600">{message.role === 'assistant' ? 'Reception AI' : 'You'}</div>
      <p className="whitespace-pre-line text-base leading-7">{message.text}</p>
    </div>
  )
}
