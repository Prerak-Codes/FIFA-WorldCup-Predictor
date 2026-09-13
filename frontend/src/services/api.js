const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function handleResponse(response) {
  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}`
    try {
      const errJson = await response.json()
      if (errJson.detail) errorMsg = errJson.detail
    } catch {
      // ignore
    }
    throw new Error(errorMsg)
  }
  return response.json()
}

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`)
  return handleResponse(res)
}

export async function getTeams() {
  const res = await fetch(`${API_BASE}/api/teams`)
  return handleResponse(res)
}

export async function predictMatchup(homeTeam, awayTeam, neutralVenue = true) {
  const res = await fetch(`${API_BASE}/api/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      home_team: homeTeam,
      away_team: awayTeam,
      neutral_venue: neutralVenue,
    }),
  })
  return handleResponse(res)
}

export async function simulateSingleTournament() {
  const res = await fetch(`${API_BASE}/api/simulate/single`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })
  return handleResponse(res)
}

export async function getSimulationLeaderboard() {
  const res = await fetch(`${API_BASE}/api/simulate/leaderboard`)
  return handleResponse(res)
}

export async function runMonteCarlo(nSimulations = 1000) {
  const res = await fetch(`${API_BASE}/api/simulate/monte-carlo`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ n_simulations: nSimulations }),
  })
  return handleResponse(res)
}

export async function getEloHistory(teams = []) {
  const params = teams.length ? `?teams=${encodeURIComponent(teams.join(','))}` : ''
  const res = await fetch(`${API_BASE}/api/analytics/elo-history${params}`)
  return handleResponse(res)
}

export async function getRadarComparison(teams = []) {
  const params = teams.length ? `?teams=${encodeURIComponent(teams.join(','))}` : ''
  const res = await fetch(`${API_BASE}/api/analytics/radar${params}`)
  return handleResponse(res)
}
