import { SectionHeading } from '@/components/section-heading'
import { BENCHMARK, type Horizon } from '@/lib/indra-data'

function fmtH(h: Horizon) {
  return h >= 60 ? `T+${h / 60}h` : `T+${h}m`
}

const METHODS = [
  { key: 'indra', label: 'INDRA', color: 'var(--lightning)' },
  { key: 'advection', label: 'Advection', color: 'var(--lad)' },
  { key: 'persistence', label: 'Persistence', color: 'var(--muted-foreground)' },
] as const

export function BaselineBenchmark() {
  return (
    <section id="verification" className="relative border-y border-hairline bg-panel/30">
      <div className="mx-auto max-w-7xl px-5 py-24 sm:px-8">
        <SectionHeading
          eyebrow="Verification · held-out replay"
          title="Scored against baselines it can’t game"
          description="INDRA is evaluated on held-out events — never its training data — against the two baselines every operational nowcast must beat: persistence and advection. Skill is reported with standard categorical metrics."
        />

        <div className="grid gap-4 lg:grid-cols-[1.3fr_1fr]">
          {/* CSI comparison */}
          <div className="panel-glass rounded-xl p-6">
            <div className="mb-6 flex items-center justify-between">
              <span className="eyebrow">Critical Success Index (higher is better)</span>
              <div className="flex items-center gap-3">
                {METHODS.map((m) => (
                  <span key={m.key} className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full" style={{ background: m.color }} />
                    <span className="text-xs text-muted-foreground">{m.label}</span>
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-6">
              {BENCHMARK.map((row) => (
                <div key={row.horizon}>
                  <div className="mb-2 tnum text-sm font-semibold text-foreground">{fmtH(row.horizon)}</div>
                  <div className="space-y-1.5">
                    {METHODS.map((m) => {
                      const val = row[m.key].CSI
                      return (
                        <div key={m.key} className="flex items-center gap-3">
                          <div className="h-5 flex-1 overflow-hidden rounded bg-secondary/60">
                            <div
                              className="flex h-full items-center justify-end rounded pr-2 transition-all"
                              style={{ width: `${val * 100}%`, background: m.color, opacity: m.key === 'indra' ? 1 : 0.55 }}
                            >
                              <span className="tnum text-[0.65rem] font-bold text-background">{val.toFixed(2)}</span>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* INDRA metric table */}
          <div className="panel-glass overflow-hidden rounded-xl">
            <div className="border-b border-hairline px-5 py-4">
              <span className="eyebrow">INDRA skill · full metric set</span>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-hairline text-left">
                  {['Lead', 'POD', 'FAR', 'CSI', 'ETS'].map((h) => (
                    <th key={h} className="eyebrow px-4 py-3 font-normal">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {BENCHMARK.map((row) => (
                  <tr key={row.horizon} className="border-b border-hairline/60 last:border-0">
                    <td className="tnum px-4 py-3.5 font-semibold text-foreground">{fmtH(row.horizon)}</td>
                    <td className="tnum px-4 py-3.5 text-nominal">{row.indra.POD.toFixed(2)}</td>
                    <td className="tnum px-4 py-3.5 text-storm">{row.indra.FAR.toFixed(2)}</td>
                    <td className="tnum px-4 py-3.5 text-lightning">{row.indra.CSI.toFixed(2)}</td>
                    <td className="tnum px-4 py-3.5 text-foreground">{row.indra.ETS.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="space-y-1 px-5 py-4">
              <p className="eyebrow">POD ↑ · FAR ↓ · CSI ↑ · ETS ↑</p>
              <p className="text-xs leading-relaxed text-muted-foreground">
                Metrics shown are from a synthetic replay harness for demonstration. The same harness
                accepts real held-out events without code changes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
