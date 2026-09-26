// INDRA — thin client for the FastAPI backend (app/service.py).
// Every function here fails soft: on any network/parse error it returns
// null instead of throwing, so the UI can fall back to labelled SYNTHETIC
// demo data rather than crashing the page.

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000'

export interface BackendHealth {
  status: string
  model: Record<string, unknown>
}

export interface ForecastResponse {
  provenance: string
  case_id: string
  latency_ms: number
  latency_target_met: boolean
  storm_cells: unknown[]
  lad_state: Record<string, unknown>
  forecast: Record<
    string,
    {
      lightning_probability: number
      thunderstorm_probability: number
      sensor_agreement: number
      pressure: number
      field: number[][]
    }
  >
  sensor_health: { source: string; status: string; provenance: string }[]
  state_summary: Record<string, unknown>
  alert_context: Record<string, unknown>
  disclaimer: string
}

async function withTimeout<T>(promise: Promise<T>, ms = 4000): Promise<T> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), ms)
  try {
    return await promise
  } finally {
    clearTimeout(timer)
  }
}

/** GET /health — used purely as a connectivity probe for the UI status pill. */
export async function getBackendHealth(): Promise<BackendHealth | null> {
  try {
    const res = await withTimeout(fetch(`${API_BASE}/health`, { cache: 'no-store' }))
    if (!res.ok) return null
    return (await res.json()) as BackendHealth
  } catch {
    return null
  }
}

/**
 * POST /forecast — asks the real model for a live nowcast.
 * Uses provenance "SYNTHETIC" by default so it works with zero real sensor
 * payloads (the backend's own default), which is enough to prove the wire
 * is live end-to-end without requiring authorized radar/satellite feeds.
 */
export async function postForecast(params: {
  district: string
  state: string
  caseId?: string
}): Promise<ForecastResponse | null> {
  try {
    const res = await withTimeout(
      fetch(`${API_BASE}/forecast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provenance: 'SYNTHETIC',
          district: params.district,
          state: params.state,
          case_id: params.caseId,
        }),
      }),
      6000,
    )
    if (!res.ok) return null
    return (await res.json()) as ForecastResponse
  } catch {
    return null
  }
}
