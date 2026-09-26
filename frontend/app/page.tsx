import { MissionBar } from '@/components/mission-bar'
import { Hero } from '@/components/hero'
import { KpiStrip } from '@/components/kpi-strip'
import { OperationsConsole } from '@/components/operations-console'
import { TrustPipeline } from '@/components/trust-pipeline'
import { EvidenceFabric } from '@/components/evidence-fabric'
import { ForecasterReview } from '@/components/forecaster-review'
import { BaselineBenchmark } from '@/components/baseline-benchmark'
import { ProvenanceFooter } from '@/components/provenance-footer'
import { buildStatePaths } from '@/lib/india-geo'

export default function Page() {
  const statePaths = buildStatePaths()

  return (
    <main className="relative">
      <MissionBar />
      <Hero />
      <KpiStrip />
      <OperationsConsole statePaths={statePaths} />
      <TrustPipeline />
      <EvidenceFabric />
      <ForecasterReview />
      <BaselineBenchmark />
      <ProvenanceFooter />
    </main>
  )
}
