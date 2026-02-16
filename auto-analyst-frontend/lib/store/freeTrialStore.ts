import { useCredits } from '@/lib/contexts/credit-context'
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface FreeTrialStore {
  queriesUsed: number
  incrementQueries: () => void
  resetQueries: () => void
  hasFreeTrial: () => boolean
  setHasFreeTrial: (value: boolean) => void
  demoMode: boolean
  setDemoMode: (value: boolean) => void
}

export const useFreeTrialStore = create<FreeTrialStore>()(
  persist(
    (set, get) => ({
      queriesUsed: 0,
      demoMode: true, // Always set demo mode to true
      incrementQueries: () => set((state: FreeTrialStore) => ({ queriesUsed: state.queriesUsed + 1 })),
      resetQueries: () => set({ queriesUsed: 0 }),
      setHasFreeTrial: (value: boolean) => set({ demoMode: value }),
      setDemoMode: (value: boolean) => set({ demoMode: value }),
      hasFreeTrial: () => {
        // Always return true in demo mode
        if (get().demoMode) {
          return true
        }
        
        // Check if user is authenticated (either admin or Google)
        const isAuthenticated = 
          (typeof localStorage !== 'undefined' && localStorage.getItem('isAdmin') === 'true') || 
          (typeof document !== 'undefined' && document.cookie.includes('next-auth.session-token'))
        
        // If authenticated, check credits instead of free trial limit
        if (isAuthenticated) {
          return true
        }
        
        // For unauthenticated users, check free trial limit
        const freeTrialLimit = process.env.NEXT_PUBLIC_FREE_TRIAL_LIMIT || '2'
        return get().queriesUsed < parseInt(freeTrialLimit)
      },
    }),
    {
      name: 'free-trial-storage',
    }
  )
) 