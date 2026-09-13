import React, { useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts'
import { Activity, Shield, TrendingUp, Plus, X } from 'lucide-react'
import { getFlagUrl } from '../utils/teams'

const PALETTE = [
  '#f59e0b', // Amber
  '#38bdf8', // Sky
  '#ec4899', // Pink
  '#10b981', // Emerald
  '#a855f7', // Purple
  '#f97316', // Orange
  '#6366f1', // Indigo
  '#14b8a6', // Teal
]

export default function AnalyticsTab({
  teams,
  eloHistory,
  radarData,
  selectedTeams,
  onToggleTeam,
  loadingElo,
  loadingRadar,
}) {
  const [activePreset, setActivePreset] = useState('favorites')

  const presets = {
    favorites: ['Spain', 'Brazil', 'Argentina', 'England'],
    europe: ['France', 'Germany', 'Spain', 'Portugal', 'Netherlands'],
    americas: ['Argentina', 'Brazil', 'Uruguay', 'Colombia', 'United States'],
  }

  const handleSelectPreset = (key) => {
    setActivePreset(key)
    const presetTeams = presets[key]
    presetTeams.forEach((t) => {
      if (!selectedTeams.includes(t)) onToggleTeam(t)
    })
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Team Selection Panel */}
      <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              Historical Team Analytics & Elo Rating Engine
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Select national teams to compare historical Elo rating curves (1990–2026) and tactical attributes.
            </p>
          </div>

          {/* Quick Presets */}
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-500 font-semibold uppercase">Presets:</span>
            <button
              onClick={() => handleSelectPreset('favorites')}
              className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition cursor-pointer"
            >
              Top Contenders
            </button>
            <button
              onClick={() => handleSelectPreset('europe')}
              className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition cursor-pointer"
            >
              Europe Heavyweights
            </button>
            <button
              onClick={() => handleSelectPreset('americas')}
              className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition cursor-pointer"
            >
              Americas
            </button>
          </div>
        </div>

        {/* Selected Team Chips */}
        <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-800/80">
          {teams.map((t) => {
            const isSelected = selectedTeams.includes(t)
            const colorIdx = selectedTeams.indexOf(t)
            const chipColor = isSelected ? PALETTE[colorIdx % PALETTE.length] : null

            return (
              <button
                key={t}
                onClick={() => onToggleTeam(t)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition cursor-pointer border ${
                  isSelected
                    ? 'bg-slate-800 text-white border-slate-600 shadow-sm'
                    : 'bg-slate-950/60 text-slate-400 border-slate-800/80 hover:bg-slate-900 hover:text-slate-200'
                }`}
                style={isSelected ? { borderColor: chipColor } : {}}
              >
                {getFlagUrl(t) && (
                  <img src={getFlagUrl(t)} alt={t} className="w-3.5 h-2.5 rounded object-cover" />
                )}
                <span>{t}</span>
                {isSelected ? (
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: chipColor }}
                  />
                ) : (
                  <Plus className="w-3 h-3 text-slate-500" />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Historical Elo Progression Line Chart */}
      <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-amber-400" />
              <span>Historical Elo Rating Trajectory (1990 – 2026)</span>
            </h3>
            <p className="text-xs text-slate-400">
              Elo ratings capture game-by-game strength updates weighted by margin of victory and tournament importance.
            </p>
          </div>
          {loadingElo && <div className="text-xs text-amber-400 animate-pulse">Loading Elo data...</div>}
        </div>

        <div className="h-80 w-full">
          {eloHistory && eloHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={eloHistory} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
                <XAxis
                  dataKey="date"
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                  tickFormatter={(val) => val.slice(0, 4)}
                />
                <YAxis
                  domain={['dataMin - 50', 'dataMax + 50']}
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                />
                <Legend />
                {selectedTeams.map((team, idx) => (
                  <Line
                    key={team}
                    type="monotone"
                    dataKey={team}
                    stroke={PALETTE[idx % PALETTE.length]}
                    strokeWidth={2}
                    dot={false}
                    connectNulls
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-sm text-slate-500">
              Select teams above to display Elo ratings trajectory.
            </div>
          )}
        </div>
      </div>

      {/* Team Metrics Detailed Comparison Table */}
      {radarData && radarData.length > 0 && (
        <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-4">
          <h3 className="text-lg font-bold text-white tracking-tight flex items-center space-x-2">
            <Shield className="w-5 h-5 text-amber-400" />
            <span>Selected Teams Attribute Comparison</span>
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                  <th className="pb-3">Team</th>
                  <th className="pb-3 text-right">Current Elo</th>
                  <th className="pb-3 text-right">FIFA Rank</th>
                  <th className="pb-3 text-right">Win Rate</th>
                  <th className="pb-3 text-right">Goals / Match</th>
                  <th className="pb-3 text-right">Conceded / Match</th>
                  <th className="pb-3 text-right">Clean Sheet %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-medium">
                {radarData.map((item, idx) => (
                  <tr key={item.team} className="hover:bg-slate-800/40 transition">
                    <td className="py-3 text-white flex items-center space-x-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                        style={{ backgroundColor: PALETTE[idx % PALETTE.length] }}
                      />
                      {getFlagUrl(item.team) && (
                        <img
                          src={getFlagUrl(item.team)}
                          alt={item.team}
                          className="w-4 h-3 rounded object-cover"
                        />
                      )}
                      <span className="font-semibold text-sm">{item.team}</span>
                    </td>
                    <td className="py-3 text-right font-bold text-amber-400">{item.elo_rating}</td>
                    <td className="py-3 text-right text-slate-200">#{item.fifa_rank}</td>
                    <td className="py-3 text-right text-emerald-400">{item.win_rate_pct}%</td>
                    <td className="py-3 text-right text-slate-200">{item.goals_scored_per_match}</td>
                    <td className="py-3 text-right text-rose-400">{item.goals_conceded_per_match}</td>
                    <td className="py-3 text-right text-sky-400">{item.clean_sheet_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
