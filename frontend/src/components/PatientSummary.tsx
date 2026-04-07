interface SummaryProps {
  name: string
  age: string
  query: string
  ward: string
  timestamp: string
}

const badgeStyles: Record<string, string> = {
  'General Ward': 'bg-emerald-100 text-emerald-800',
  'Emergency Ward': 'bg-rose-100 text-rose-800',
  'Mental Health Ward': 'bg-violet-100 text-violet-800',
}

export default function PatientSummary({ name, age, query, ward, timestamp }: SummaryProps) {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-chat">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Patient summary</h2>
          <p className="mt-1 text-sm text-slate-500">The registration details are complete and securely stored.</p>
        </div>
        <span className={`rounded-full px-4 py-2 text-sm font-semibold ${badgeStyles[ward] || 'bg-slate-100 text-slate-800'}`}>
          {ward}
        </span>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl bg-slate-50 p-4">
          <dt className="text-xs uppercase tracking-[0.2em] text-slate-500">Name</dt>
          <dd className="mt-2 text-base font-medium text-slate-900">{name}</dd>
        </div>
        <div className="rounded-2xl bg-slate-50 p-4">
          <dt className="text-xs uppercase tracking-[0.2em] text-slate-500">Age</dt>
          <dd className="mt-2 text-base font-medium text-slate-900">{age}</dd>
        </div>
        <div className="sm:col-span-2 rounded-2xl bg-slate-50 p-4">
          <dt className="text-xs uppercase tracking-[0.2em] text-slate-500">Query</dt>
          <dd className="mt-2 text-base font-medium text-slate-900">{query}</dd>
        </div>
        <div className="sm:col-span-2 text-sm text-slate-500">
          <span className="font-medium">Registered at:</span> {new Date(timestamp).toLocaleString()}
        </div>
      </div>
    </section>
  )
}
