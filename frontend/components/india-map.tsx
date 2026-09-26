'use client'

import { CELLS, GEO, project, severityColor, type Horizon, type StormCell } from '@/lib/indra-data'
import type { StatePath } from '@/lib/india-geo'

const COMPASS: Record<string, number> = {
  N: 0, NNE: 22.5, NE: 45, ENE: 67.5, E: 90, ESE: 112.5, SE: 135, SSE: 157.5,
  S: 180, SSW: 202.5, SW: 225, WSW: 247.5, W: 270, WNW: 292.5, NW: 315, NNW: 337.5,
}

export type MapLayer = 'risk' | 'cells' | 'tracks' | 'lightning'

function motionVector(cell: StormCell) {
  const angle = ((COMPASS[cell.motionDir] ?? 45) * Math.PI) / 180
  const { x, y } = project(cell.lon, cell.lat)
  const len = 60 + cell.motionSpeed * 2.6
  return {
    x, y,
    ex: x + Math.sin(angle) * len,
    ey: y - Math.cos(angle) * len,
    angle: COMPASS[cell.motionDir] ?? 45,
  }
}

interface Props {
  statePaths: StatePath[]
  selectedId: string
  horizon: Horizon
  layer: MapLayer
  onSelect: (id: string) => void
}

export function IndiaMap({ statePaths, selectedId, horizon, layer, onSelect }: Props) {
  const graticuleLon = [70, 75, 80, 85, 90, 95]
  const graticuleLat = [10, 15, 20, 25, 30, 35]

  return (
    <div className="relative aspect-[1000/1077] w-full overflow-hidden rounded-lg">
      {/* radar sweep */}
      <div className="pointer-events-none absolute left-1/2 top-1/2 aspect-square w-[130%] -translate-x-1/2 -translate-y-1/2 rounded-full opacity-40">
        <div
          className="animate-radar h-full w-full rounded-full"
          style={{
            background:
              'conic-gradient(from 0deg, transparent 0deg, transparent 300deg, oklch(0.83 0.15 202 / 0.18) 350deg, oklch(0.83 0.15 202 / 0.42) 360deg)',
            maskImage: 'radial-gradient(circle, black 62%, transparent 63%)',
            WebkitMaskImage: 'radial-gradient(circle, black 62%, transparent 63%)',
          }}
        />
      </div>

      <svg
        viewBox={`0 0 ${GEO.width} ${GEO.height}`}
        className="relative h-full w-full"
        role="img"
        aria-label="Operational map of India showing tracked convective storm cells"
      >
        <defs>
          <radialGradient id="bloom-severe" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="oklch(0.66 0.22 18)" stopOpacity="0.7" />
            <stop offset="100%" stopColor="oklch(0.66 0.22 18)" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="bloom-high" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="oklch(0.8 0.15 66)" stopOpacity="0.6" />
            <stop offset="100%" stopColor="oklch(0.8 0.15 66)" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="bloom-moderate" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="oklch(0.83 0.15 202)" stopOpacity="0.5" />
            <stop offset="100%" stopColor="oklch(0.83 0.15 202)" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="bloom-low" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="oklch(0.66 0.02 245)" stopOpacity="0.4" />
            <stop offset="100%" stopColor="oklch(0.66 0.02 245)" stopOpacity="0" />
          </radialGradient>
          <filter id="soft-glow" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="6" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* graticule */}
        <g stroke="oklch(0.92 0.02 240 / 0.06)" strokeWidth="1">
          {graticuleLon.map((lon) => {
            const a = project(lon, GEO.latMax)
            const b = project(lon, GEO.latMin)
            return <line key={`lon-${lon}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} />
          })}
          {graticuleLat.map((lat) => {
            const a = project(GEO.lonMin, lat)
            const b = project(GEO.lonMax, lat)
            return <line key={`lat-${lat}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} />
          })}
        </g>

        {/* state polygons */}
        <g>
          {statePaths.map((s) => (
            <path
              key={s.name}
              d={s.d}
              fill="oklch(0.22 0.025 255 / 0.55)"
              stroke="oklch(0.83 0.15 202 / 0.22)"
              strokeWidth="1.1"
              strokeLinejoin="round"
            />
          ))}
        </g>

        {/* risk field blooms */}
        {(layer === 'risk' || layer === 'cells') && (
          <g>
            {CELLS.map((c) => {
              const { x, y } = project(c.lon, c.lat)
              const p = c.storm[horizon] / 100
              const r = (70 + c.area * 7) * (0.6 + p * 0.8)
              return (
                <circle
                  key={`bloom-${c.id}`}
                  cx={x}
                  cy={y}
                  r={r}
                  fill={`url(#bloom-${c.severity})`}
                  opacity={layer === 'risk' ? 0.55 + p * 0.4 : 0.28}
                />
              )
            })}
          </g>
        )}

        {/* motion tracks + uncertainty cones */}
        {layer === 'tracks' &&
          CELLS.map((c) => {
            const v = motionVector(c)
            const spread = 26 + c.growth
            const perp = ((v.angle + 90) * Math.PI) / 180
            const px = Math.cos(perp) * spread
            const py = Math.sin(perp) * spread
            return (
              <g key={`trk-${c.id}`}>
                <path
                  d={`M${v.x} ${v.y} L${v.ex + px} ${v.ey + py} L${v.ex - px} ${v.ey - py} Z`}
                  fill="oklch(0.83 0.15 202 / 0.1)"
                  stroke="oklch(0.83 0.15 202 / 0.25)"
                  strokeWidth="1"
                />
                <line
                  x1={v.x}
                  y1={v.y}
                  x2={v.ex}
                  y2={v.ey}
                  stroke="oklch(0.83 0.15 202 / 0.8)"
                  strokeWidth="2"
                  strokeDasharray="6 6"
                  style={{ animation: 'dash 30s linear infinite' }}
                />
                <circle cx={v.ex} cy={v.ey} r="4" fill="oklch(0.83 0.15 202)" />
              </g>
            )
          })}

        {/* lightning glyphs */}
        {layer === 'lightning' &&
          CELLS.map((c) => {
            const { x, y } = project(c.lon, c.lat)
            const flashes = Math.round(c.lad * 6)
            return (
              <g key={`lt-${c.id}`} filter="url(#soft-glow)">
                {Array.from({ length: flashes }).map((_, i) => {
                  const ang = (i / flashes) * Math.PI * 2
                  const rad = 18 + (i % 3) * 22
                  const fx = x + Math.cos(ang) * rad
                  const fy = y + Math.sin(ang) * rad
                  return (
                    <circle
                      key={i}
                      cx={fx}
                      cy={fy}
                      r="3"
                      fill="oklch(0.83 0.15 202)"
                      className="animate-pulse-soft"
                      style={{ animationDelay: `${(i % 5) * 0.25}s` }}
                    />
                  )
                })}
              </g>
            )
          })}

        {/* cell markers */}
        <g>
          {CELLS.map((c) => {
            const { x, y } = project(c.lon, c.lat)
            const selected = c.id === selectedId
            const color = severityColor[c.severity]
            return (
              <g
                key={c.id}
                transform={`translate(${x} ${y})`}
                className="cursor-pointer"
                onClick={() => onSelect(c.id)}
                role="button"
                aria-label={`Select storm cell ${c.id} over ${c.city}`}
              >
                {selected && (
                  <>
                    <circle r="26" fill="none" stroke={color} strokeWidth="1.5" opacity="0.5" />
                    <circle r="26" fill="none" stroke={color} strokeWidth="2" className="animate-ping-ring" style={{ transformOrigin: 'center' }} />
                  </>
                )}
                <circle r="9" fill={color} filter="url(#soft-glow)" />
                <circle r="9" fill="none" stroke="white" strokeOpacity={selected ? 0.9 : 0.3} strokeWidth="1.5" />
                <circle r="3.5" fill="white" fillOpacity="0.9" />
                {/* crosshair for selected */}
                {selected && (
                  <g stroke={color} strokeWidth="1.5" opacity="0.8">
                    <line x1="-18" y1="0" x2="-11" y2="0" />
                    <line x1="11" y1="0" x2="18" y2="0" />
                    <line x1="0" y1="-18" x2="0" y2="-11" />
                    <line x1="0" y1="11" x2="0" y2="18" />
                  </g>
                )}
                <text
                  x="16"
                  y="-10"
                  fill="oklch(0.94 0.008 240)"
                  fontSize="17"
                  fontFamily="var(--font-jetbrains)"
                  fontWeight={selected ? 700 : 500}
                  style={{ letterSpacing: '0.5px' }}
                >
                  {c.id}
                </text>
                <text
                  x="16"
                  y="9"
                  fill={color}
                  fontSize="13"
                  fontFamily="var(--font-jetbrains)"
                  style={{ letterSpacing: '1px' }}
                >
                  {c.city.toUpperCase()}
                </text>
              </g>
            )
          })}
        </g>
      </svg>
    </div>
  )
}
