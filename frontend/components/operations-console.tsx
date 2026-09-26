'use client'

import { useMemo, useState } from 'react'
import { Activity, Cloud, Radar, Waypoints, Zap, TriangleAlert, ArrowUpRight, Satellite, Loader2 } from 'lucide-react'
import { IndiaMap, type MapLayer } from '@/components/india-map'
import { TemporalOutlook } from '@/components/temporal-outlook'
import { SectionHeading } from '@/components/section-heading'
import {
  CELLS,
  HORIZONS,
  severityColor,
  severityLabel,
  type Horizon,
} from '@/lib/indra-data'
import { postForecast, type ForecastResponse } from '@/lib/api'
import type { StatePath } from '@/lib/india-geo'

const LAYERS: { key: MapLayer; label: string; icon: typeof Radar }[] = [
  { key: 'risk', label: 'Risk field', icon: Cloud },
  { key: 'cells', label: 'Storm cells', icon: Radar },
  { key: 'tracks', label: 'Motion tracks', icon: Waypoints },
  { key: 'lightning', label: 'Lightning', icon: Zap },
]

function fmtHorizon(h: Horizon) {
  return h >= 60 ? `${h / 60}h` : `${h}m`
}

export function OperationsConsole({ statePaths }: { statePaths: StatePath[] }) {
  const [selectedId, setSelectedId] = useState('C-1055')
  const [horizon, setHorizon] = useState<Horizon>(30)
  const [layer, setLayer] = useState<MapLayer>('risk')
  const [liveResult, setLiveResult] = useState<ForecastResponse | null>(null)
  const [liveLoading, setLiveLoading] = useState(false)
  const [liveError, setLiveError] = useState(false)

  const cell = useMemo(() => CELLS.find((c) => c.id === selectedId)!, [selectedId])
  const color = severityColor[cell.severity]

  async function runLiveForecast() {
    setLiveLoading(true)
    setLiveError(false)
    const result = await postForecast({ district: cell.city, state: cell.state, caseId: cell.id })
    setLiveLoading(false)
    if (result) setLiveResult(result)
    else setLiveError(true)
  }

  return (
    <section id="console" className="relative mx-auto max-w-7xl px-5 py-24 sm:px-8">
      <SectionHeading
        eyebrow="Operations console"
        title="A working nowcast, not a slide"
        description="Select a tracked cell and a lead time. Every field is separated by source so a forecaster can see what was observed versus what was inferred."
      />

      {/* toolbar */}
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="flex flex-wrap items-center gap-1 rounded-lg border border-hairline bg-panel/60 p-1">
          {LAYERS.map((l) => {
            const active = layer === l.key
            const Icon = l.icon
            return (
              <button
                key={l.key}
                onClick={() => setLayer(l.key)}
                className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-medium transition ${
                  active
                    ? 'bg-primary/15 text-primary'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
                aria-pressed={active}
              >
                <Icon className="h-3.5 w-3.5" />
                {l.label}
              </button>
            )
          })}
        </div>

        <div className="flex items-center gap-1 rounded-lg border border-hairline bg-panel/60 p-1">
          <span className="eyebrow px-2">Lead</span>
          {HORIZONS.map((h) => {
            const active = horizon === h
            return (
              <button
                key={h}
                onClick={() => setHorizon(h)}
                className={`tnum rounded-md px-2.5 py-1.5 text-xs transition ${
                  active ? 'bg-primary/15 text-primary' : 'text-muted-foreground hover:text-foreground'
                }`}
                aria-pressed={active}
              >
                {fmtHorizon(h)}
              </button>
            )
          })}
        </div>

        <button
          onClick={runLiveForecast}
          disabled={liveLoading}
          className="flex items-center gap-2 rounded-full border border-primary/40 bg-primary/10 px-3 py-1.5 text-primary transition hover:bg-primary/20 disabled:opacity-60"
        >
          {liveLoading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Satellite className="h-3.5 w-3.5" />
          )}
          <span className="eyebrow !text-primary">Ping live backend</span>
        </button>

        <div className="ml-auto flex items-center gap-2 rounded-full border border-storm/40 bg-storm/10 px-3 py-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-storm animate-pulse-soft" />
          <span className="eyebrow !text-storm">Synthetic replay</span>
        </div>
      </div>

      {(liveResult || liveError) && (
        <div
          className={`mb-4 flex flex-wrap items-center gap-x-6 gap-y-2 rounded-lg border px-4 py-3 ${
            liveError ? 'border-destructive/40 bg-destructive/5' : 'border-nominal/40 bg-nominal/5'
          }`}
        >
          {liveError ? (
            <p className="text-xs text-muted-foreground">
              Couldn&apos;t reach the FastAPI backend at{' '}
              <code className="text-foreground">{process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}</code>.
              Run <code className="text-foreground">uvicorn app.service:app --reload</code> and try again.
            </p>
          ) : liveResult ? (
            <>
              <span className="eyebrow !text-nominal">Live backend response</span>
              <span className="tnum text-xs text-muted-foreground">
                latency <span className="text-foreground">{liveResult.latency_ms} ms</span>
              </span>
              <span className="tnum text-xs text-muted-foreground">
                case <span className="text-foreground">{liveResult.case_id}</span>
              </span>
              {liveResult.forecast[String(horizon)] && (
                <>
                  <span className="tnum text-xs text-muted-foreground">
                    P(flash) lead {fmtHorizon(horizon)}{' '}
                    <span className="text-foreground">
                      {(liveResult.forecast[String(horizon)].lightning_probability * 100).toFixed(1)}%
                    </span>
                  </span>
                  <span className="tnum text-xs text-muted-foreground">
                    sensor agreement{' '}
                    <span className="text-foreground">
                      {(liveResult.forecast[String(horizon)].sensor_agreement * 100).toFixed(0)}%
                    </span>
                  </span>
                </>
              )}
            </>
          ) : null}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-[1.6fr_1fr]">
        {/* map */}
        <div className="panel-glass relative overflow-hidden rounded-xl p-3">
          <div className="mb-2 flex items-center justify-between px-1">
            <div className="flex items-center gap-2">
              <Radar className="h-4 w-4 text-primary" />
              <span className="eyebrow">INDRA · convective field · India domain</span>
            </div>
            <span className="tnum text-xs text-muted-foreground">
              25.9°N · lead {fmtHorizon(horizon)}
            </span>
          </div>
          <IndiaMap
            statePaths={statePaths}
            selectedId={selectedId}
            horizon={horizon}
            layer={layer}
            onSelect={setSelectedId}
          />
          {/* map footer legend */}
          <div className="mt-2 flex flex-wrap items-center gap-x-5 gap-y-2 px-1">
            {(['severe', 'high', 'moderate', 'low'] as const).map((s) => (
              <span key={s} className="flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full" style={{ background: severityColor[s] }} />
                <span className="eyebrow">{severityLabel[s]}</span>
              </span>
            ))}
          </div>
        </div>

        {/* inspector */}
        <div className="panel-glass flex flex-col overflow-hidden rounded-xl">
          <div className="flex items-center justify-between border-b border-hairline px-4 py-3">
            <div>
              <div className="tnum text-lg font-bold text-foreground">{cell.id}</div>
              <div className="text-xs text-muted-foreground">
                {cell.city}, {cell.state}
              </div>
            </div>
            <span
              className="rounded-full px-2.5 py-1 text-[0.62rem] font-bold tracking-widest"
              style={{ color, background: `color-mix(in oklch, ${color} 16%, transparent)` }}
            >
              {severityLabel[cell.severity]}
            </span>
          </div>

          {/* headline probabilities */}
          <div className="grid grid-cols-2 divide-x divide-hairline border-b border-hairline">
            <div className="p-4">
              <div className="flex items-center gap-1.5">
                <Zap className="h-3.5 w-3.5 text-lightning" />
                <span className="eyebrow">Lightning</span>
              </div>
              <div className="tnum mt-1 text-3xl font-bold text-lightning text-glow-cyan">
                {cell.lightning[horizon]}
                <span className="text-lg text-muted-foreground">%</span>
              </div>
              <div className="eyebrow mt-0.5">P(flash) · {fmtHorizon(horizon)}</div>
            </div>
            <div className="p-4">
              <div className="flex items-center gap-1.5">
                <Cloud className="h-3.5 w-3.5 text-storm" />
                <span className="eyebrow">Thunderstorm</span>
              </div>
              <div className="tnum mt-1 text-3xl font-bold text-storm">
                {cell.storm[horizon]}
                <span className="text-lg text-muted-foreground">%</span>
              </div>
              <div className="eyebrow mt-0.5">P(convection) · {fmtHorizon(horizon)}</div>
            </div>
          </div>

          {/* attributes */}
          <div className="grid grid-cols-2 gap-px bg-hairline">
            {[
              { icon: Activity, label: 'Peak Z', value: `${cell.intensity} dBZ` },
              { icon: ArrowUpRight, label: 'Echo-top growth', value: `+${cell.growth}%` },
              { icon: Waypoints, label: 'Motion', value: `${cell.motionDir} · ${cell.motionSpeed} km/h` },
              { icon: Zap, label: 'LAD pressure', value: cell.lad.toFixed(2) },
            ].map((a) => (
              <div key={a.label} className="bg-panel p-4">
                <div className="flex items-center gap-1.5 text-muted-foreground">
                  <a.icon className="h-3.5 w-3.5" />
                  <span className="eyebrow">{a.label}</span>
                </div>
                <div className="tnum mt-1 text-base font-semibold text-foreground">{a.value}</div>
              </div>
            ))}
          </div>

          {/* provenance / confidence */}
          <div className="mt-auto space-y-3 p-4">
            <div className="eyebrow">Source contribution</div>
            <SignalBar label="Radar (DWR)" value={82} tone="lightning" note="synthetic" />
            <SignalBar label="NWP (WRF)" value={71} tone="nominal" note="current" />
            <SignalBar label="Lightning (ILLN)" value={38} tone="storm" note="+11m delayed" />
            <SignalBar label="Satellite (INSAT)" value={0} tone="danger" note="missing" />
            <div className="flex gap-2 rounded-lg border border-storm/30 bg-storm/5 p-3">
              <TriangleAlert className="mt-0.5 h-4 w-4 shrink-0 text-storm" />
              <p className="text-xs leading-relaxed text-muted-foreground">
                Satellite payload is <span className="text-foreground">missing</span>, so vertical
                growth confidence is down-weighted. INDRA surfaces this — it never fabricates the
                absent channel.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* temporal outlook */}
      <TemporalOutlook cell={cell} horizon={horizon} onHorizon={setHorizon} />
    </section>
  )
}

function SignalBar({
  label,
  value,
  tone,
  note,
}: {
  label: string
  value: number
  tone: 'lightning' | 'storm' | 'nominal' | 'danger'
  note: string
}) {
  const toneVar = `var(--${tone})`
  return (
    <div>
      <div className="mb-1 flex items-center justify-between">
        <span className="text-xs text-foreground">{label}</span>
        <span className="eyebrow" style={{ color: value === 0 ? 'var(--danger)' : undefined }}>
          {note}
        </span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${Math.max(value, 3)}%`, background: toneVar, opacity: value === 0 ? 0.3 : 1 }}
        />
      </div>
    </div>
  )
}
