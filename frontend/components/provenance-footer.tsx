import { IndraMark } from '@/components/mission-bar'

export function ProvenanceFooter() {
  return (
    <footer className="relative overflow-hidden border-t border-hairline bg-space">
      <div className="grid-overlay pointer-events-none absolute inset-0 opacity-40" />
      <div className="relative mx-auto max-w-7xl px-5 py-16 sm:px-8">
        <div className="grid gap-10 lg:grid-cols-[1.4fr_1fr_1fr]">
          <div>
            <div className="flex items-center gap-2.5">
              <IndraMark className="h-8 w-8" />
              <span className="font-display text-lg font-bold tracking-[0.2em]">INDRA</span>
            </div>
            <p className="mt-4 max-w-sm text-sm leading-relaxed text-muted-foreground">
              Provenance-first convective intelligence for 0–3 hour thunderstorm and lightning
              nowcasting over India. Built for Smart India Hackathon · NTRO problem statement 26072.
            </p>
            <div className="mt-5 inline-flex items-center gap-2 rounded-full border border-storm/40 bg-storm/10 px-3 py-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-storm" />
              <span className="eyebrow !text-storm">Synthetic demonstration data</span>
            </div>
          </div>

          <FootCol
            title="Console"
            links={[
              ['Operations', '#console'],
              ['Method', '#method'],
              ['Evidence', '#evidence'],
              ['Verification', '#verification'],
            ]}
          />
          <FootCol
            title="Data lineage"
            links={[
              ['IMD Doppler Radar', '#evidence'],
              ['INSAT-3D · MOSDAC', '#evidence'],
              ['IITM ILLN Lightning', '#evidence'],
              ['IMD WRF / EWRF', '#evidence'],
            ]}
          />
        </div>

        <div className="mt-12 flex flex-col gap-4 border-t border-hairline pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="max-w-2xl text-xs leading-relaxed text-muted-foreground">
            Decision-support prototype. Not an official forecast or warning product. Nowcasts shown
            are illustrative; INDRA never issues warnings autonomously — authorized forecasters do.
          </p>
          <p className="tnum shrink-0 text-xs text-muted-foreground">© {new Date().getFullYear()} Team INDRA</p>
        </div>
      </div>
    </footer>
  )
}

function FootCol({ title, links }: { title: string; links: [string, string][] }) {
  return (
    <div>
      <div className="eyebrow mb-3">{title}</div>
      <ul className="space-y-2">
        {links.map(([label, href]) => (
          <li key={label}>
            <a href={href} className="text-sm text-muted-foreground transition hover:text-foreground">
              {label}
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}
