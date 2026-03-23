export interface AgentResult {
  agent_name: 'patent' | 'clinical' | 'web_intel' | 
              'insights' | 'molecular_validator'
  status: 'running' | 'done' | 'failed'
  result: string
  duration_ms?: number
}

export interface ResearchResponse {
  run_id: string
  status: string
  report_path?: string
  agents: AgentResult[]
  molecular_validation?: {
    confidence_score: number
    admet: {
      absorption: number
      distribution: number
      metabolism: number
      excretion: number
      toxicity: number
    }
    binding_affinity: string
    target_protein: string
    rationale: string
  }
}
