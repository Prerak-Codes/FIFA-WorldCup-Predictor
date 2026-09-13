import React, { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import PredictorTab from './components/PredictorTab'
import BracketSimulatorTab from './components/BracketSimulatorTab'
import AnalyticsTab from './components/AnalyticsTab'
import {
  checkHealth,
  getTeams,
  predictMatchup,
  simulateSingleTournament,
  getSimulationLeaderboard,
  getEloHistory,
  getRadarComparison,
} from './services/api'

export default function App() {
  const [activeTab, setActiveTab] = useState('predictor') // 'predictor' | 'simulator' | 'analytics'
  const [apiStatus, setApiStatus] = useState('checking') // 'checking' | 'online' | 'offline'

  // Data states
  const [teams, setTeams] = useState([
    'Spain', 'England', 'Brazil', 'Argentina', 'France', 'Germany',
    'Netherlands', 'Portugal', 'Belgium', 'Uruguay', 'Croatia', 'United States'
  ])

  // Predictor state
  const [prediction, setPrediction] = useState(null)
  const [loadingPredict, setLoadingPredict] = useState(false)
  const [predictError, setPredictError] = useState(null)

  // Simulation state
  const [singleSim, setSingleSim] = useState(null)
  const [leaderboard, setLeaderboard] = useState(null)
  const [loadingSingle, setLoadingSingle] = useState(false)

  // Analytics state
  const [selectedTeams, setSelectedTeams] = useState(['Spain', 'Brazil', 'Argentina', 'England'])
  const [eloHistory, setEloHistory] = useState([])
  const [radarData, setRadarData] = useState([])
  const [loadingElo, setLoadingElo] = useState(false)
  const [loadingRadar, setLoadingRadar] = useState(false)

  // Initial Bootstrapping
  useEffect(() => {
    async function init() {
      try {
        await checkHealth()
        setApiStatus('online')
      } catch (err) {
        console.warn('Backend offline or not reachable:', err)
        setApiStatus('offline')
      }

      // Fetch teams
      try {
        const teamsData = await getTeams()
        if (teamsData?.teams?.length) {
          setTeams(teamsData.teams)
        }
      } catch (err) {
        console.error('Failed to load teams:', err)
      }

      // Fetch initial prediction
      try {
        const initialPred = await predictMatchup('Spain', 'England', true)
        setPrediction(initialPred)
      } catch (err) {
        console.error('Failed to load initial prediction:', err)
      }

      // Fetch single bracket simulation
      try {
        const sim = await simulateSingleTournament()
        setSingleSim(sim)
      } catch (err) {
        console.error('Failed to load single simulation:', err)
      }

      // Fetch simulation leaderboard
      try {
        const lb = await getSimulationLeaderboard()
        if (lb?.leaderboard) {
          setLeaderboard(lb.leaderboard)
        }
      } catch (err) {
        console.error('Failed to load simulation leaderboard:', err)
      }

      // Fetch analytics for initial teams
      loadAnalytics(['Spain', 'Brazil', 'Argentina', 'England'])
    }

    init()
  }, [])

  const loadAnalytics = async (teamList) => {
    if (!teamList || teamList.length === 0) {
      setEloHistory([])
      setRadarData([])
      return
    }

    setLoadingElo(true)
    setLoadingRadar(true)

    try {
      const eloRes = await getEloHistory(teamList)
      setEloHistory(eloRes?.history || [])
    } catch (err) {
      console.error('Failed to load Elo history:', err)
    } finally {
      setLoadingElo(false)
    }

    try {
      const radarRes = await getRadarComparison(teamList)
      setRadarData(radarRes?.metrics || [])
    } catch (err) {
      console.error('Failed to load radar metrics:', err)
    } finally {
      setLoadingRadar(false)
    }
  }

  const handlePredict = async (home, away, neutral) => {
    setLoadingPredict(true)
    setPredictError(null)
    try {
      const res = await predictMatchup(home, away, neutral)
      setPrediction(res)
    } catch (err) {
      setPredictError(err.message || 'Prediction failed. Check backend connection.')
    } finally {
      setLoadingPredict(false)
    }
  }

  const handleRunSingleSim = async () => {
    setLoadingSingle(true)
    try {
      const res = await simulateSingleTournament()
      setSingleSim(res)
    } catch (err) {
      console.error('Single simulation failed:', err)
    } finally {
      setLoadingSingle(false)
    }
  }

  const handleToggleTeam = (team) => {
    let updated
    if (selectedTeams.includes(team)) {
      if (selectedTeams.length <= 1) return // Keep at least one team
      updated = selectedTeams.filter((t) => t !== team)
    } else {
      if (selectedTeams.length >= 8) {
        updated = [...selectedTeams.slice(1), team] // Cap at 8
      } else {
        updated = [...selectedTeams, team]
      }
    }
    setSelectedTeams(updated)
    loadAnalytics(updated)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-amber-500/30 selection:text-amber-200">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} apiStatus={apiStatus} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'predictor' && (
          <PredictorTab
            teams={teams}
            onPredict={handlePredict}
            prediction={prediction}
            loading={loadingPredict}
            error={predictError}
          />
        )}

        {activeTab === 'simulator' && (
          <BracketSimulatorTab
            singleSim={singleSim}
            leaderboard={leaderboard}
            onRunSingleSim={handleRunSingleSim}
            loadingSingle={loadingSingle}
            loadingLeaderboard={false}
          />
        )}

        {activeTab === 'analytics' && (
          <AnalyticsTab
            teams={teams}
            eloHistory={eloHistory}
            radarData={radarData}
            selectedTeams={selectedTeams}
            onToggleTeam={handleToggleTeam}
            loadingElo={loadingElo}
            loadingRadar={loadingRadar}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/60 py-6 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            FIFA World Cup 2026 AI Predictor &middot; Decoupled Full-Stack Architecture
          </div>
          <div className="flex items-center space-x-4">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="text-slate-400 hover:text-amber-400 transition"
            >
              FastAPI Interactive Docs (Swagger)
            </a>
            <span>&middot;</span>
            <span className="text-slate-400">XGBoost &bull; Monte Carlo &bull; Vite &bull; React</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
