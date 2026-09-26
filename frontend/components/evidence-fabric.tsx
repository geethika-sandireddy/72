import { CheckCircle2, CircleDashed, Clock, XCircle } from 'lucide-react'
import { SectionHeading } from '@/components/section-heading'
import { SOURCES, type SourceState } from '@/lib/indra-data'

const STATE_META: Record<
  SourceState,
  { label: string; tone: string; icon: typeof CheckCircle2 }
> = {
  ready: { label: 'Available', tone: 'nominal', icon: CheckCircle2 },
  synthetic: { label: 'Synthetic', tone: 'lightning', icon: CircleDashed },
  delayed: { label: 'Delayed', tone: 'storm', icon: Clock },
  missing: { label: 'Missing', tone: 'danger', icon: XCircle },
}

export function EvidenceFabric() {
  return (
    <section id="evidence" className="relative border-y border-hairline bg-panel/30">
      <div className="mx-auto max-w-7xl px-5 py-24 sm:px-8">
        <SectionHeading
          eyebrow="Evidence fabric"
          title="Honest about what it actually sees"
          description="Each modality reports its own health. When a feed is missing or stale, INDRA down-weights it and says so — the single most trust-destroying failure in operational nowcasting is pretending data exists."
        />

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {SOURCES.map((s) => {
            const meta = STATE_META[s.state]
            const Icon = meta.icon
            return (
              <div key={s.key} className="panel-glass flex flex-col rounded-xl p-5">
                <div className="flex items-center justify-between">
                  <h3 className="font-display text-lg font-semibold text-foreground">{s.label}</h3>
                  <span
                    className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[0.62rem] font-bold tracking-widest"
                    style={{
                      color: `var(--${meta.tone})`,
                      background: `color-mix(in oklch, var(--${meta.tone}) 14%, transparent)`,
                    }}
                  >
                    <Icon className="h-3 w-3" />
                    {meta.label.toUpperCase()}
                  </span>
                </div>
                <div className="mt-4 space-y-2 border-t border-hairline pt-4">
                  <Row k="Product" v={s.product} />
                  <Row k="Network" v={s.network} />
                  <Row k="Freshness" v={s.freshness} tone={s.state === 'missing' ? 'danger' : undefined} />
                </div>
                <p className="mt-4 text-xs leading-relaxed text-muted-foreground">{s.note}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

function Row({ k, v, tone }: { k: string; v: string; tone?: string }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <span className="eyebrow shrink-0">{k}</span>
      <span
        className="tnum text-right text-xs"
        style={{ color: tone ? `var(--${tone})` : 'var(--foreground)' }}
      >
        {v}
      </span>
    </div>
  )
}
