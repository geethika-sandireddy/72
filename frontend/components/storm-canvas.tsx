'use client'

import { useEffect, useRef } from 'react'

interface Drop {
  x: number
  y: number
  len: number
  speed: number
  o: number
}
interface Cell {
  x: number
  y: number
  r: number
  phase: number
  hue: 'cyan' | 'amber' | 'violet'
}

const HUES: Record<Cell['hue'], string> = {
  cyan: '131, 224, 255',
  amber: '255, 178, 71',
  violet: '167, 139, 250',
}

export function StormCanvas() {
  const ref = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    let raf = 0
    let w = 0
    let h = 0
    let dpr = 1

    let drops: Drop[] = []
    let cells: Cell[] = []
    let bolt: { pts: { x: number; y: number }[]; life: number } | null = null
    let flash = 0
    let nextBolt = 60

    const resize = () => {
      dpr = Math.min(window.devicePixelRatio || 1, 2)
      w = canvas.clientWidth
      h = canvas.clientHeight
      canvas.width = w * dpr
      canvas.height = h * dpr
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

      drops = Array.from({ length: Math.round((w * h) / 14000) }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        len: 8 + Math.random() * 18,
        speed: 3 + Math.random() * 6,
        o: 0.05 + Math.random() * 0.15,
      }))
      const hues: Cell['hue'][] = ['cyan', 'amber', 'violet']
      cells = Array.from({ length: 6 }, (_, i) => ({
        x: (w / 6) * (i + 0.5) + (Math.random() - 0.5) * 80,
        y: h * (0.3 + Math.random() * 0.5),
        r: 90 + Math.random() * 140,
        phase: Math.random() * Math.PI * 2,
        hue: hues[i % 3],
      }))
    }

    const makeBolt = () => {
      const x = w * (0.2 + Math.random() * 0.6)
      const pts = [{ x, y: -10 }]
      let cy = -10
      let cx = x
      while (cy < h * (0.55 + Math.random() * 0.3)) {
        cy += 18 + Math.random() * 34
        cx += (Math.random() - 0.5) * 60
        pts.push({ x: cx, y: cy })
      }
      bolt = { pts, life: 1 }
      flash = 0.5
    }

    let t = 0
    const draw = () => {
      t += 1
      ctx.clearRect(0, 0, w, h)

      // convective blobs
      cells.forEach((c) => {
        const pulse = 0.5 + 0.5 * Math.sin(t * 0.01 + c.phase)
        const r = c.r * (0.85 + pulse * 0.25)
        const g = ctx.createRadialGradient(c.x, c.y, 0, c.x, c.y, r)
        const rgb = HUES[c.hue]
        g.addColorStop(0, `rgba(${rgb}, ${0.1 + pulse * 0.08})`)
        g.addColorStop(1, `rgba(${rgb}, 0)`)
        ctx.fillStyle = g
        ctx.beginPath()
        ctx.arc(c.x, c.y, r, 0, Math.PI * 2)
        ctx.fill()
        if (!reduced) {
          c.x += Math.sin(t * 0.004 + c.phase) * 0.15
          c.y += Math.cos(t * 0.003 + c.phase) * 0.08
        }
      })

      // rain
      ctx.lineCap = 'round'
      drops.forEach((d) => {
        ctx.strokeStyle = `rgba(131, 224, 255, ${d.o})`
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(d.x, d.y)
        ctx.lineTo(d.x - 1.5, d.y + d.len)
        ctx.stroke()
        if (!reduced) {
          d.y += d.speed
          d.x -= 0.4
          if (d.y > h) {
            d.y = -d.len
            d.x = Math.random() * w
          }
        }
      })

      // lightning
      if (!reduced) {
        nextBolt -= 1
        if (nextBolt <= 0 && !bolt) {
          makeBolt()
          nextBolt = 140 + Math.random() * 220
        }
      }
      if (flash > 0) {
        ctx.fillStyle = `rgba(131, 224, 255, ${flash * 0.06})`
        ctx.fillRect(0, 0, w, h)
        flash -= 0.04
      }
      if (bolt) {
        ctx.strokeStyle = `rgba(190, 240, 255, ${bolt.life})`
        ctx.lineWidth = 2
        ctx.shadowBlur = 18
        ctx.shadowColor = 'rgba(131, 224, 255, 0.9)'
        ctx.beginPath()
        bolt.pts.forEach((p, i) => (i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y)))
        ctx.stroke()
        ctx.shadowBlur = 0
        bolt.life -= 0.05
        if (bolt.life <= 0) bolt = null
      }

      raf = requestAnimationFrame(draw)
    }

    resize()
    window.addEventListener('resize', resize)
    if (reduced) {
      draw()
    } else {
      raf = requestAnimationFrame(draw)
    }

    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return <canvas ref={ref} className="absolute inset-0 h-full w-full" aria-hidden="true" />
}
