import { SectionHeading } from '@/components/section-heading'
import { PIPELINE } from '@/lib/indra-data'

export function TrustPipeline() {
  return (
    <section id="method" className="relative mx-auto max-w-7xl px-5 py-24 sm:px-8">
      <SectionHeading
        eyebrow="Method · provenance-first"
        title="Trust is engineered, not asserted"
        description="INDRA is a pipeline where every stage is inspectable. Observation is kept separate from inference, so a forecaster always knows why a number is what it is."
      />

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {PIPELINE.map((p, i) => (
          <div
            key={p.step}
            className="panel-glass group relative overflow-hidden rounded-xl p-5 transition hover:-translate-y-0.5"
          >
            <div
              className="absolute inset-x-0 top-0 h-px opacity-60"
              style={{ background: `linear-gradient(90deg, transparent, var(--${p.color}), transparent)` }}
            />
            <div className="flex items-center justify-between">
              <span className="tnum text-xs text-muted-foreground">{p.step}</span>
              <span
                className="h-2 w-2 rounded-full"
                style={{ background: `var(--${p.color})`, boxShadow: `0 0 12px var(--${p.color})` }}
              />
            </div>
            <h3 className="mt-6 font-display text-lg font-semibold text-foreground">{p.title}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{p.desc}</p>
            {i < PIPELINE.length - 1 && (
              <span className="pointer-events-none absolute -right-1.5 top-1/2 hidden h-3 w-3 -translate-y-1/2 rotate-45 border-r border-t border-hairline bg-panel lg:block" />
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
