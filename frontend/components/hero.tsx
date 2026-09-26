'use client'

import { ArrowDown, Radar, ShieldCheck, Zap } from 'lucide-react'
import { StormCanvas } from '@/components/storm-canvas'

const TICKER = [
  'IMD DOPPLER RADAR',
  'INSAT-3D / 3DR · MOSDAC',
  'IITM ILLN LIGHTNING',
  'IMD WRF / EWRF · NCUM',
  'PROVENANCE-FIRST FUSION',
  'HELD-OUT REPLAY VERIFICATION',
  'POD · FAR · CSI · ETS',
  'DECISION SUPPORT · NOT AUTO-WARNING',
]

export function Hero() {
  return (
    <section className="relative flex min-h-screen flex-col justify-center overflow-hidden bg-space pt-24">
      <StormCanvas />
      <div className="grid-overlay pointer-events-none absolute inset-0 opacity-60" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-background to-transparent" />

      <div className="relative mx-auto w-full max-w-7xl px-5 sm:px-8">
        <div className="max-w-3xl animate-rise">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-hairline bg-background/50 px-3 py-1.5 backdrop-blur-sm">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-lightning opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-lightning" />
            </span>
            <span className="eyebrow">Convective nowcasting · 0–3 hour horizon</span>
          </div>

          <h1 className="text-balance font-display text-5xl font-bold leading-[1.02] tracking-tight text-foreground sm:text-6xl lg:text-7xl">
            See the storm
            <br />
            <span className="bg-gradient-to-r from-lightning via-primary to-lad bg-clip-text text-transparent text-glow-cyan">
              before it strikes.
            </span>
          </h1>

          <p className="mt-6 max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">
            INDRA fuses radar, satellite, lightning and NWP into a single provenance-first console for
            thunderstorm and lightning nowcasting over India — engineered so a forecaster can trust,
            question and act on every field.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-3">
            <a
              href="#console"
              className="glow-cyan group inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition hover:opacity-90"
            >
              <Radar className="h-4 w-4" />
              Enter the console
              <ArrowDown className="h-4 w-4 transition group-hover:translate-y-0.5" />
            </a>
            <a
              href="#method"
              className="inline-flex items-center gap-2 rounded-full border border-hairline bg-background/40 px-6 py-3 text-sm font-semibold text-foreground backdrop-blur-sm transition hover:bg-secondary"
            >
              How it earns trust
            </a>
          </div>

          <div className="mt-10 flex flex-wrap gap-x-8 gap-y-4">
            {[
              { icon: Zap, k: 'Hazards, separated', v: 'Lightning ≠ thunderstorm' },
              { icon: ShieldCheck, k: 'Missing data', v: 'Surfaced, never faked' },
              { icon: Radar, k: 'Verification', v: 'Held-out POD/FAR/CSI/ETS' },
            ].map((f) => (
              <div key={f.k} className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-hairline bg-background/40">
                  <f.icon className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <div className="text-sm font-semibold text-foreground">{f.k}</div>
                  <div className="eyebrow">{f.v}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ticker */}
      <div className="relative mt-16 overflow-hidden border-y border-hairline bg-background/40 py-3 backdrop-blur-sm">
        <div className="animate-marquee flex w-max gap-8 whitespace-nowrap">
          {[...TICKER, ...TICKER].map((item, i) => (
            <span key={i} className="flex items-center gap-8 eyebrow">
              {item}
              <span className="h-1 w-1 rounded-full bg-primary/50" />
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}
