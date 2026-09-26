// INDRA — deterministic SYNTHETIC demonstration data.
// Every value here is demo-only and explicitly labelled SYNTHETIC in the UI.
// Nothing in this module claims real-time skill, calibration, or official warning status.

export type Severity = 'severe' | 'high' | 'moderate' | 'low'
export type Provenance = 'SYNTHETIC' | 'REPLAY' | 'LIVE'
export type SourceState = 'ready' | 'synthetic' | 'delayed' | 'missing'

export const HORIZONS = [5, 15, 30, 60, 180] as const
export type Horizon = (typeof HORIZONS)[number]

// India geographic bounds (padded) used for the operations projection.
export const GEO = {
  lonMin: 67.0,
  lonMax: 98.5,
  latMin: 6.0,
  latMax: 37.5,
  width: 1000,
  // height derived from an equirectangular correction at India's mean latitude
  height: 1077,
}

/** Project geographic lon/lat into the map viewBox coordinate space. */
export function project(lon: number, lat: number): { x: number; y: number } {
  const x = ((lon - GEO.lonMin) / (GEO.lonMax - GEO.lonMin)) * GEO.width
  const y = ((GEO.latMax - lat) / (GEO.latMax - GEO.latMin)) * GEO.height
  return { x, y }
}

export interface StormCell {
  id: string
  city: string
  state: string
  lat: number
  lon: number
  severity: Severity
  intensity: number // dBZ
  growth: number // % echo-top growth
  motionDir: string
  motionSpeed: number // km/h
  area: number // grid cells
  lad: number // Lightning Activity Density pressure state
  /** per-horizon lightning / thunderstorm probability (%) */
  lightning: Record<Horizon, number>
  storm: Record<Horizon, number>
}

export const CELLS: StormCell[] = [
  {
    id: 'C-1042',
    city: 'Patna',
    state: 'Bihar',
    lat: 25.61,
    lon: 85.14,
    severity: 'high',
    intensity: 62,
    growth: 31,
    motionDir: 'NE',
    motionSpeed: 38,
    area: 14,
    lad: 1.82,
    lightning: { 5: 48, 15: 61, 30: 71, 60: 58, 180: 33 },
    storm: { 5: 37, 15: 52, 30: 71, 60: 63, 180: 41 },
  },
  {
    id: 'C-1055',
    city: 'Guwahati',
    state: 'Assam',
    lat: 26.14,
    lon: 91.73,
    severity: 'severe',
    intensity: 68,
    growth: 44,
    motionDir: 'ENE',
    motionSpeed: 46,
    area: 21,
    lad: 2.31,
    lightning: { 5: 66, 15: 78, 30: 84, 60: 69, 180: 40 },
    storm: { 5: 52, 15: 71, 30: 82, 60: 74, 180: 48 },
  },
  {
    id: 'C-1047',
    city: 'Nagpur',
    state: 'Maharashtra',
    lat: 21.14,
    lon: 79.09,
    severity: 'moderate',
    intensity: 54,
    growth: 18,
    motionDir: 'NNE',
    motionSpeed: 29,
    area: 9,
    lad: 1.24,
    lightning: { 5: 34, 15: 44, 30: 52, 60: 47, 180: 26 },
    storm: { 5: 29, 15: 38, 30: 49, 60: 45, 180: 30 },
  },
  {
    id: 'C-1039',
    city: 'Hyderabad',
    state: 'Telangana',
    lat: 17.38,
    lon: 78.48,
    severity: 'moderate',
    intensity: 51,
    growth: 12,
    motionDir: 'N',
    motionSpeed: 24,
    area: 7,
    lad: 0.98,
    lightning: { 5: 28, 15: 36, 30: 43, 60: 39, 180: 22 },
    storm: { 5: 24, 15: 33, 30: 41, 60: 38, 180: 25 },
  },
  {
    id: 'C-1061',
    city: 'Kolkata',
    state: 'West Bengal',
    lat: 22.57,
    lon: 88.36,
    severity: 'low',
    intensity: 43,
    growth: 6,
    motionDir: 'E',
    motionSpeed: 19,
    area: 5,
    lad: 0.61,
    lightning: { 5: 18, 15: 24, 30: 29, 60: 26, 180: 15 },
    storm: { 5: 16, 15: 22, 30: 27, 60: 24, 180: 17 },
  },
]

export interface SourceFeed {
  key: string
  label: string
  product: string
  network: string
  state: SourceState
  freshness: string
  note: string
}

export const SOURCES: SourceFeed[] = [
  {
    key: 'radar',
    label: 'Radar',
    product: 'PPI-Z · MAX-Z · PPI-V',
    network: 'IMD Doppler Weather Radar',
    state: 'synthetic',
    freshness: 'demo field',
    note: 'Deterministic reflectivity field for interaction testing.',
  },
  {
    key: 'satellite',
    label: 'Satellite',
    product: 'TIR-1 · WV · CMV',
    network: 'INSAT-3D / 3DR via MOSDAC',
    state: 'missing',
    freshness: 'no payload',
    note: 'No authorized payload connected — treated as missing, not assumed.',
  },
  {
    key: 'lightning',
    label: 'Lightning',
    product: 'Flash density · rate jumps',
    network: 'IITM ILLN / IMD',
    state: 'delayed',
    freshness: '+11 min',
    note: 'Feed delayed beyond the sync window; contribution down-weighted.',
  },
  {
    key: 'nwp',
    label: 'NWP',
    product: 'CAPE · CIN · shear · RH',
    network: 'IMD WRF / EWRF · NCUM',
    state: 'ready',
    freshness: 'current',
    note: 'Thermodynamic environment available for the analysis window.',
  },
]

// Held-out replay verification — INDRA vs persistence & advection baselines.
export type Metric = 'POD' | 'FAR' | 'CSI' | 'ETS'
export interface BenchmarkRow {
  horizon: Horizon
  indra: Record<Metric, number>
  persistence: Record<Metric, number>
  advection: Record<Metric, number>
}

export const BENCHMARK: BenchmarkRow[] = [
  {
    horizon: 15,
    indra: { POD: 0.86, FAR: 0.21, CSI: 0.71, ETS: 0.58 },
    persistence: { POD: 0.74, FAR: 0.38, CSI: 0.52, ETS: 0.39 },
    advection: { POD: 0.79, FAR: 0.31, CSI: 0.6, ETS: 0.46 },
  },
  {
    horizon: 30,
    indra: { POD: 0.81, FAR: 0.26, CSI: 0.64, ETS: 0.5 },
    persistence: { POD: 0.63, FAR: 0.47, CSI: 0.41, ETS: 0.28 },
    advection: { POD: 0.72, FAR: 0.37, CSI: 0.52, ETS: 0.38 },
  },
  {
    horizon: 60,
    indra: { POD: 0.73, FAR: 0.34, CSI: 0.54, ETS: 0.41 },
    persistence: { POD: 0.49, FAR: 0.58, CSI: 0.29, ETS: 0.17 },
    advection: { POD: 0.61, FAR: 0.45, CSI: 0.41, ETS: 0.28 },
  },
]

export const PIPELINE = [
  { step: '01', title: 'Source health', desc: 'Availability & freshness per modality', color: 'lightning' },
  { step: '02', title: 'QC / evidence', desc: 'Separate what was observed from what agrees', color: 'lightning' },
  { step: '03', title: 'Storm object', desc: 'Track cell dynamics, growth & motion', color: 'storm' },
  { step: '04', title: 'LAD state', desc: 'Lightning Activity Density pressure', color: 'lad' },
  { step: '05', title: 'Hazard fields', desc: 'Lightning & thunderstorm forecast separately', color: 'storm' },
  { step: '06', title: 'Baseline compare', desc: 'Persistence · advection · INDRA', color: 'nominal' },
  { step: '07', title: 'Human review', desc: 'Decision support — never auto-warning', color: 'lad' },
  { step: '08', title: 'Replay verify', desc: 'Auditable held-out POD/FAR/CSI/ETS', color: 'nominal' },
] as const

export const severityColor: Record<Severity, string> = {
  severe: 'var(--danger)',
  high: 'var(--storm)',
  moderate: 'var(--lightning)',
  low: 'var(--muted-foreground)',
}

export const severityLabel: Record<Severity, string> = {
  severe: 'SEVERE',
  high: 'HIGH',
  moderate: 'MODERATE',
  low: 'LOW',
}
