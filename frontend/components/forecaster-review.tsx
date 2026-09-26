'use client'

import { useState } from 'react'
import { Check, Flag, PencilLine, ShieldCheck, UserCheck } from 'lucide-react'
import { SectionHeading } from '@/components/section-heading'

type Action = 'accept' | 'annotate' | 'escalate'

const ACTIONS: { key: Action; label: string; icon: typeof Check; tone: string }[] = [
  { key: 'accept', label: 'Accept nowcast', icon: Check, tone: 'nominal' },
  { key: 'annotate', label: 'Annotate & adjust', icon: PencilLine, tone: 'lightning' },
  { key: 'escalate', label: 'Escalate to warning desk', icon: Flag, tone: 'danger' },
]

const OUTCOME: Record<Action, string> = {
  accept: 'Nowcast logged as-is. Provenance snapshot and source health are attached to the record for later replay.',
  annotate: 'Forecaster note stored alongside the machine output. Both the model field and the human adjustment remain independently auditable.',
  escalate: 'Routed to the warning desk with full evidence. INDRA prepares the case — the authorized forecaster issues the warning, never the model.',
}

export function ForecasterReview() {
  const [action, setAction] = useState<Action>('annotate')

  return (
    <section className="relative mx-auto max-w-7xl px-5 py-24 sm:px-8">
      <div className="grid items-center gap-10 lg:grid-cols-2">
        <div>
          <SectionHeading
            eyebrow="Human in command"
            title="Decision support — never an auto-warning"
            description="INDRA assembles the evidence and proposes; an authorized forecaster decides. The loop is designed so accountability always rests with a person, and every action is captured for audit."
          />
          <ul className="space-y-3">
            {[
              'The model surfaces confidence and its gaps, not a single unquestioned verdict.',
              'Human adjustments are stored beside machine output — neither overwrites the other.',
              'Warnings are issued by people; INDRA only prepares a defensible case.',
            ].map((t) => (
              <li key={t} className="flex items-start gap-2.5 text-sm text-muted-foreground">
                <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                <span>{t}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="panel-glass overflow-hidden rounded-2xl">
          <div className="flex items-center justify-between border-b border-hairline px-5 py-4">
            <div className="flex items-center gap-2">
              <UserCheck className="h-4 w-4 text-primary" />
              <span className="eyebrow">Forecaster review · C-1055 Guwahati</span>
            </div>
            <span className="rounded-full bg-danger/15 px-2.5 py-1 text-[0.62rem] font-bold tracking-widest text-danger">
              SEVERE
            </span>
          </div>

          <div className="space-y-4 p-5">
            <p className="text-sm leading-relaxed text-foreground">
              INDRA proposes a <span className="text-storm">rapidly intensifying</span> cell with{' '}
              <span className="tnum text-lightning">84%</span> lightning probability at 30 min. Satellite
              is missing, so vertical-growth confidence is flagged. Recommend forecaster review.
            </p>

            <div className="grid gap-2 sm:grid-cols-3">
              {ACTIONS.map((a) => {
                const active = action === a.key
                const Icon = a.icon
                return (
                  <button
                    key={a.key}
                    onClick={() => setAction(a.key)}
                    className="flex items-center gap-2 rounded-lg border px-3 py-2.5 text-left text-xs font-medium transition"
                    style={{
                      borderColor: active ? `var(--${a.tone})` : 'var(--hairline)',
                      background: active ? `color-mix(in oklch, var(--${a.tone}) 12%, transparent)` : 'transparent',
                      color: active ? `var(--${a.tone})` : 'var(--muted-foreground)',
                    }}
                    aria-pressed={active}
                  >
                    <Icon className="h-3.5 w-3.5 shrink-0" />
                    {a.label}
                  </button>
                )
              })}
            </div>

            <div className="rounded-lg border border-hairline bg-background/40 p-4">
              <div className="eyebrow mb-1.5">Outcome</div>
              <p className="text-sm leading-relaxed text-muted-foreground">{OUTCOME[action]}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
