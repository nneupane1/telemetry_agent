import Link from "next/link"
import { useRouter } from "next/router"
import { useEffect, useState } from "react"

import NeonNavbar from "../../components/NeonNavbar"
import { fetchCohortList } from "../../services/apiClient"

export default function CohortIndexPage() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    fetchCohortList()
      .then((cohorts) => {
        if (!active) return
        const firstCohortId = cohorts[0]?.cohort_id
        if (firstCohortId) {
          void router.replace(`/cohort/${encodeURIComponent(firstCohortId)}`)
          return
        }
        setError("No cohorts are currently available.")
      })
      .catch(() => {
        if (!active) return
        setError("Unable to load cohort registry.")
      })

    return () => {
      active = false
    }
  }, [router])

  return (
    <>
      <NeonNavbar />
      <main className="max-w-5xl mx-auto px-6 py-12">
        <section className="panel panel-glow p-6 space-y-2">
          <h1 className="text-2xl">Cohort Intelligence</h1>
          <p className="text-sm text-text-secondary">
            Resolving available cohorts from the backend registry.
          </p>
          {error ? (
            <p className="text-sm text-danger">{error}</p>
          ) : (
            <p className="text-sm text-text-secondary">Loading...</p>
          )}
          <Link href="/" className="chip-cyan inline-flex">
            Back to Overview
          </Link>
        </section>
      </main>
    </>
  )
}
