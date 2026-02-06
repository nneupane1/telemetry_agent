import { create } from "zustand"

import {
  fetchCohortList,
  fetchCohortInterpretation,
  fetchVinInterpretation,
  VinInterpretation,
} from "../services/apiClient"

export const defaultVinQueue = [
  "WVWZZZ1KZ6W000001",
  "WVWZZZ1KZ6W000002",
  "WVWZZZ1KZ6W000003",
]

export function riskScoreFromLevel(risk: string) {
  if (risk === "LOW") return 88
  if (risk === "ELEVATED") return 68
  if (risk === "HIGH") return 46
  return 25
}

interface ExecutiveDashboardState {
  vinData: VinInterpretation[]
  cohortSummary: string
  loading: boolean
  error: string | null
  cinematicMode: boolean
  selectedVin: string | null
  toggleCinematicMode: () => void
  setSelectedVin: (vin: string | null) => void
  loadOverview: (vins?: string[]) => Promise<void>
}

export const useExecutiveDashboardStore = create<ExecutiveDashboardState>((set, get) => ({
  vinData: [],
  cohortSummary: "Loading cohort interpretation...",
  loading: true,
  error: null,
  cinematicMode: true,
  selectedVin: null,

  toggleCinematicMode: () =>
    set((state) => ({ cinematicMode: !state.cinematicMode })),

  setSelectedVin: (vin) => set({ selectedVin: vin }),

  loadOverview: async (vins = defaultVinQueue) => {
    set({ loading: true, error: null })

    const results = await Promise.allSettled(
      vins.map((vin) => fetchVinInterpretation(vin))
    )

    const vinData = results
      .filter(
        (result): result is PromiseFulfilledResult<VinInterpretation> =>
          result.status === "fulfilled"
      )
      .map((result) => result.value)

    let cohortSummary = "Cohort interpretation is currently unavailable."
    try {
      const cohorts = await fetchCohortList()
      const primaryCohortId = cohorts[0]?.cohort_id
      if (primaryCohortId) {
        const cohort = await fetchCohortInterpretation(primaryCohortId)
        cohortSummary = cohort.summary
      } else {
        cohortSummary = "No cohorts are currently available."
      }
    } catch {
      // Summary fallback is already set.
    }

    const existingSelectedVin = get().selectedVin
    const selectedVin =
      existingSelectedVin && vinData.some((row) => row.vin === existingSelectedVin)
        ? existingSelectedVin
        : vinData[0]?.vin ?? null

    set({
      vinData,
      cohortSummary,
      loading: false,
      error:
        vinData.length === 0
          ? "No VIN interpretations were returned by the API."
          : null,
      selectedVin,
    })
  },
}))
