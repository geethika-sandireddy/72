const KPIS = [
  { value: '0–3h', label: 'Nowcast horizon', sub: 'the gap models miss' },
  { value: '4', label: 'Fused modalities', sub: 'radar · sat · lightning · NWP' },
  { value: '+0.23', label: 'CSI vs persistence', sub: 'held-out replay · 30 min' },
  { value: '8', label: 'Provenance stages', sub: 'source → verify, all auditable' },
  { value: '100%', label: 'Reproducible', sub: 'replayable, no black box' },
]

export function KpiStrip() {
  return (
    <section className="border-y border-hairline bg-panel/40">
      <div className="mx-auto grid max-w-7xl grid-cols-2 divide-x divide-hairline sm:grid-cols-3 lg:grid-cols-5">
        {KPIS.map((k, i) => (
          <div
            key={k.label}
            className={`px-5 py-7 sm:px-6 ${i >= 3 ? 'border-t border-hairline lg:border-t-0' : ''} ${
              i === 2 ? 'border-t border-hairline sm:border-t-0' : ''
            }`}
          >
            <div className="tnum text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              {k.value}
            </div>
            <div className="mt-1 text-sm font-medium text-foreground">{k.label}</div>
            <div className="eyebrow mt-0.5">{k.sub}</div>
          </div>
        ))}
      </div>
    </section>
  )
}
