'use client'

import { useEffect, useState } from 'react'
import { getBackendHealth } from '@/lib/api'

const NAV = [
  { label: 'Console', href: '#console' },
  { label: 'Method', href: '#method' },
  { label: 'Evidence', href: '#evidence' },
  { label: 'Verification', href: '#verification' },
]

export function IndraMark({ className = 'h-7 w-7' }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
      <defs>
        <linearGradient id="mark" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="oklch(0.86 0.15 202)" />
          <stop offset="100%" stopColor="oklch(0.72 0.16 292)" />
        </linearGradient>
      </defs>
      <path
        d="M16 2 L28 9 V20 C28 25 22 29 16 30 C10 29 4 25 4 20 V9 Z"
        fill="none"
        stroke="url(#mark)"
        strokeWidth="1.6"
        opacity="0.9"
      />
      <path d="M17.5 8 L11 17 H15.5 L14 24 L21 14.5 H16.5 Z" fill="url(#mark)" />
    </svg>
  )
}

export function MissionBar() {
  const [now, setNow] = useState<string>('')
  const [backendUp, setBackendUp] = useState<boolean | null>(null)

  useEffect(() => {
    const tick = () => {
      const d = new Date()
      setNow(
        d.toLocaleTimeString('en-GB', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          timeZone: 'UTC',
        }),
      )
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    let cancelled = false
    const check = async () => {
      const health = await getBackendHealth()
      if (!cancelled) setBackendUp(!!health)
    }
    check()
    const id = setInterval(check, 15000)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  return (
    <header className="fixed inset-x-0 top-0 z-50">
      <div className="mx-auto flex max-w-7xl items-center gap-4 px-5 py-3 sm:px-8">
        <div className="flex items-center gap-2.5 rounded-full border border-hairline bg-background/70 px-3 py-1.5 backdrop-blur-md">
          <IndraMark className="h-6 w-6" />
          <span className="font-display text-sm font-bold tracking-[0.2em] text-foreground">INDRA</span>
        </div>

        <nav className="hidden items-center gap-1 rounded-full border border-hairline bg-background/70 px-1.5 py-1.5 backdrop-blur-md md:flex">
          {NAV.map((n) => (
            <a
              key={n.href}
              href={n.href}
              className="rounded-full px-3 py-1 text-sm text-muted-foreground transition hover:bg-secondary hover:text-foreground"
            >
              {n.label}
            </a>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <div className="hidden items-center gap-2 rounded-full border border-hairline bg-background/70 px-3 py-1.5 backdrop-blur-md sm:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-nominal animate-pulse-soft" />
            <span className="tnum text-xs text-muted-foreground">{now || '--:--:--'} UTC</span>
          </div>
          <div
            className={`hidden items-center gap-2 rounded-full border px-3 py-1.5 backdrop-blur-md sm:flex ${
              backendUp
                ? 'border-nominal/30 bg-nominal/10'
                : 'border-hairline bg-background/70'
            }`}
            title={backendUp ? 'FastAPI backend reachable' : 'Backend unreachable — showing synthetic data'}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                backendUp === null
                  ? 'bg-muted-foreground'
                  : backendUp
                    ? 'bg-nominal animate-pulse-soft'
                    : 'bg-destructive'
              }`}
            />
            <span className="eyebrow">
              {backendUp === null ? 'CHECKING BACKEND' : backendUp ? 'BACKEND LIVE' : 'BACKEND OFFLINE'}
            </span>
          </div>
          <div className="rounded-full border border-primary/30 bg-primary/10 px-3 py-1.5">
            <span className="eyebrow !text-primary">NTRO · PS 26072</span>
          </div>
        </div>
      </div>
    </header>
  )
}
