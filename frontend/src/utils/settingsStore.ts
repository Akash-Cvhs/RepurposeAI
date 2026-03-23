import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Settings {
  isDark: boolean
  accentColor: string
  compactMode: boolean
  apiUrl: string
  requestTimeout: number
  autoSave: boolean
  agents: {
    patent: boolean
    clinical: boolean
    web: boolean
    insights: boolean
    molecular: boolean
  }
  setIsDark: (v: boolean) => void
  setAccentColor: (v: string) => void
  setCompactMode: (v: boolean) => void
  setApiUrl: (v: string) => void
  setRequestTimeout: (v: number) => void
  setAutoSave: (v: boolean) => void
  setAgent: (name: string, v: boolean) => void
}

export const useSettingsStore = create<Settings>()(
  persist(
    (set) => ({
      isDark: false,
      accentColor: '#E85D24',
      compactMode: false,
      apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      requestTimeout: 300000,
      autoSave: true,
      agents: {
        patent: true,
        clinical: true,
        web: true,
        insights: true,
        molecular: true
      },
      setIsDark: (v) => set({ isDark: v }),
      setAccentColor: (v) => set({ accentColor: v }),
      setCompactMode: (v) => set({ compactMode: v }),
      setApiUrl: (v) => set({ apiUrl: v }),
      setRequestTimeout: (v) => set({ requestTimeout: v }),
      setAutoSave: (v) => set({ autoSave: v }),
      setAgent: (name, v) => set((s) => ({
        agents: { ...s.agents, [name]: v }
      }))
    }),
    { name: 'repurpose-ai-settings' }
  )
)
