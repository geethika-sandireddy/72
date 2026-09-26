'use client'

import { HORIZONS, type Horizon, type StormCell } from '@/lib/indra-data'

const W = 820
const H = 240
const PAD = { l: 44, r: 24, t: 24, b: 34 }

function fmt(h: Horizon) {
  return h >= 60 ? `${h / 60}h` : `${h}m`
}

function points(values: number[]) {
  const n = values.length
  return values.map((v, i) => {
    const x = PAD.l + (i * (W - PAD.l - PAD.r)) / (n - 1)
    const y = PAD.t + (1 - v / 100) * (H - PAD.t - PAD.b)
    return { x, y, v }
  })
}

export function TemporalOutlook({
  cell,
  horizon,
  onHorizon,
}: {
  cell: StormCell
  horizon: Horizon
  onHorizon: (h: Horizon) => void
}) {
  const lightning = points(HORIZONS.map((h) => cell.lightning[h]))
  const storm = points(HORIZONS.map((h) => cell.storm[h]))
  const line = (pts: { x: number; y: number }[]) => pts.map((p, i) => `${i ? 'L' : 'M'}${p.x} ${p.y}`).join(' ')
  const area = (pts: { x: number; y: number }[]) =>
    `${line(pts)} L${pts[pts.length - 1].x} ${H - PAD.b} L${pts[0].x} ${H - PAD.b} Z`
  const activeIdx = HORIZONS.indexOf(horizon)
  const guideX = PAD.l + (activeIdx * (W - PAD.l - PAD.r)) / (HORIZONS.length - 1)

  return (
    <div className="panel-glass mt-4 overflow-hidden rounded-xl p-4">
      <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="eyebrow">Temporal outlook · {cell.id}</span>
        </div>
        <div className="flex items-center gap-4">
          <Legend color="var(--lightning)" label="Lightning P(flash)" />
          <Legend color="var(--storm)" label="Thunderstorm P(convection)" />
        </div>
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Probability versus lead time">
        <defs>
          <linearGradient id="fill-lightning" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="oklch(0.83 0.15 202)" stopOpacity="0.28" />
            <stop offset="100%" stopColor="oklch(0.83 0.15 202)" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="fill-storm" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="oklch(0.8 0.15 66)" stopOpacity="0.22" />
            <stop offset="100%" stopColor="oklch(0.8 0.15 66)" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* y gridlines */}
        {[0, 25, 50, 75, 100].map((g) => {
          const y = PAD.t + (1 - g / 100) * (H - PAD.t - PAD.b)
          return (
            <g key={g}>
              <line x1={PAD.l} y1={y} x2={W - PAD.r} y2={y} stroke="oklch(0.92 0.02 240 / 0.06)" />
              <text x={PAD.l - 10} y={y + 4} textAnchor="end" fontSize="11" fontFamily="var(--font-jetbrains)" fill="oklch(0.66 0.018 245)">
                {g}
              </text>
            </g>
          )
        })}

        {/* active horizon guide */}
        <line x1={guideX} y1={PAD.t} x2={guideX} y2={H - PAD.b} stroke="oklch(0.94 0.008 240 / 0.35)" strokeDasharray="4 4" />

        {/* areas + lines */}
        <path d={area(storm)} fill="url(#fill-storm)" />
        <path d={area(lightning)} fill="url(#fill-lightning)" />
        <path d={line(storm)} fill="none" stroke="var(--storm)" strokeWidth="2.5" strokeLinejoin="round" />
        <path d={line(lightning)} fill="none" stroke="var(--lightning)" strokeWidth="2.5" strokeLinejoin="round" />

        {/* interactive points */}
        {HORIZONS.map((h, i) => {
          const lx = lightning[i]
          const sx = storm[i]
          const active = h === horizon
          const axisY = H - PAD.b
          return (
            <g key={h} className="cursor-pointer" onClick={() => onHorizon(h)}>
              <rect x={lx.x - 24} y={PAD.t} width="48" height={H - PAD.t - PAD.b} fill="transparent" />
              <circle cx={sx.x} cy={sx.y} r={active ? 5 : 3.5} fill="var(--storm)" stroke="var(--background)" strokeWidth="1.5" />
              <circle cx={lx.x} cy={lx.y} r={active ? 5 : 3.5} fill="var(--lightning)" stroke="var(--background)" strokeWidth="1.5" />
              <text
                x={lx.x}
                y={axisY + 20}
                textAnchor="middle"
                fontSize="12"
                fontFamily="var(--font-jetbrains)"
                fontWeight={active ? 700 : 400}
                fill={active ? 'oklch(0.94 0.008 240)' : 'oklch(0.66 0.018 245)'}
              >
                {fmt(h)}
              </text>
            </g>
          )
        })}
      </svg>
      <p className="mt-1 px-1 text-xs text-muted-foreground">
        Skill decays with lead time — INDRA shows the decay honestly instead of flattering the 0–3 h
        curve. Click any lead time to drive the console.
      </p>
    </div>
  )
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className="h-2 w-4 rounded-full" style={{ background: color }} />
      <span className="text-xs text-muted-foreground">{label}</span>
    </span>
  )
}
