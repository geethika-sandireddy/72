import raw from '@/lib/geo/india-states.json'
import { project } from '@/lib/indra-data'

type Ring = [number, number][]

interface Feature {
  id?: string
  properties?: { name?: string }
  geometry: { type: 'Polygon' | 'MultiPolygon'; coordinates: unknown }
}

function ringToPath(ring: Ring): string {
  let d = ''
  ring.forEach(([lon, lat], i) => {
    const { x, y } = project(lon, lat)
    d += `${i === 0 ? 'M' : 'L'}${x.toFixed(1)} ${y.toFixed(1)}`
  })
  return d + 'Z'
}

export interface StatePath {
  name: string
  d: string
}

/** Precompute SVG path strings for every Indian state (runs on the server). */
export function buildStatePaths(): StatePath[] {
  const features = (raw as unknown as { features: Feature[] }).features
  return features.map((f) => {
    const { type, coordinates } = f.geometry
    let d = ''
    if (type === 'Polygon') {
      ;(coordinates as Ring[]).forEach((ring) => {
        d += ringToPath(ring)
      })
    } else {
      ;(coordinates as Ring[][]).forEach((poly) => {
        poly.forEach((ring) => {
          d += ringToPath(ring)
        })
      })
    }
    return { name: f.properties?.name ?? f.id ?? 'unknown', d }
  })
}
