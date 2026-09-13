import React, { useState } from 'react'
import { Trophy, Medal, Play, RefreshCw, BarChart2, GitFork, Check, ChevronRight } from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { getFlagUrl } from '../utils/teams'

export default function BracketSimulatorTab({
  singleSim,
  leaderboard,
  onRunSingleSim,
  loadingSingle,
  loadingLeaderboard,
}) {
  const [subView, setSubView] = useState('single') // 'single' | 'montecarlo'

  // Top 10 for bar chart
  const topContenders = leaderboard
    ? [...leaderboard]
        .sort((a, b) => b.win_pct - a.win_pct)
        .slice(0, 10)
        .map((item) => ({
          name: item.team,
          probability: item.win_pct,
        }))
    : []

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Sub-view Switcher Header */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-900/80 p-4 rounded-2xl border border-slate-800">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setSubView('single')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-semibold transition cursor-pointer ${
              subView === 'single'
                ? 'bg-amber-400 text-slate-950 shadow-md shadow-amber-400/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <GitFork className="w-4 h-4" />
            <span>Interactive Live Bracket</span>
          </button>
          <button
            onClick={() => setSubView('montecarlo')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-semibold transition cursor-pointer ${
              subView === 'montecarlo'
                ? 'bg-amber-400 text-slate-950 shadow-md shadow-amber-400/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <BarChart2 className="w-4 h-4" />
            <span>Monte Carlo Championship Odds (10,000 Runs)</span>
          </button>
        </div>

        {subView === 'single' && (
          <button
            onClick={onRunSingleSim}
            disabled={loadingSingle}
            className="w-full sm:w-auto px-5 py-2 rounded-xl text-sm font-bold bg-slate-800 hover:bg-slate-700 text-amber-400 border border-amber-400/30 hover:border-amber-400/60 transition flex items-center justify-center space-x-2 cursor-pointer shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loadingSingle ? 'animate-spin' : ''}`} />
            <span>{loadingSingle ? 'Simulating Bracket...' : 'Simulate New Tournament'}</span>
          </button>
        )}
      </div>

      {/* VIEW 1: SINGLE BRACKET SIMULATION */}
      {subView === 'single' && (
        <div className="space-y-8">
          {/* Podium / Champion Showcase */}
          {singleSim && (
            <div className="bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 rounded-2xl border border-amber-500/40 p-6 md:p-8 shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 right-1/4 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

              <div className="text-center max-w-lg mx-auto mb-6">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-amber-400/20 border border-amber-400/40 text-amber-400 mb-2 shadow-inner">
                  <Trophy className="w-7 h-7" />
                </div>
                <div className="text-xs font-bold text-amber-400 uppercase tracking-widest">
                  2026 World Champion
                </div>
                <div className="flex items-center justify-center space-x-3 mt-1">
                  {getFlagUrl(singleSim.champion) && (
                    <img
                      src={getFlagUrl(singleSim.champion)}
                      alt={singleSim.champion}
                      className="w-9 h-6 rounded shadow object-cover border border-amber-400/50"
                    />
                  )}
                  <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
                    {singleSim.champion}
                  </h2>
                </div>
              </div>

              {/* Podium Positions */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-2xl mx-auto">
                {/* 2nd Place */}
                <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3.5 text-center">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-center space-x-1">
                    <Medal className="w-3.5 h-3.5 text-slate-300" />
                    <span>Runner-Up (2nd)</span>
                  </div>
                  <div className="text-base font-bold text-slate-200 mt-1 flex items-center justify-center space-x-2">
                    {getFlagUrl(singleSim.runner_up) && (
                      <img
                        src={getFlagUrl(singleSim.runner_up)}
                        alt={singleSim.runner_up}
                        className="w-5 h-3.5 rounded object-cover"
                      />
                    )}
                    <span>{singleSim.runner_up}</span>
                  </div>
                </div>

                {/* 3rd Place */}
                <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3.5 text-center">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-center space-x-1">
                    <Medal className="w-3.5 h-3.5 text-amber-600" />
                    <span>Third Place (3rd)</span>
                  </div>
                  <div className="text-base font-bold text-slate-200 mt-1 flex items-center justify-center space-x-2">
                    {getFlagUrl(singleSim.third_place) && (
                      <img
                        src={getFlagUrl(singleSim.third_place)}
                        alt={singleSim.third_place}
                        className="w-5 h-3.5 rounded object-cover"
                      />
                    )}
                    <span>{singleSim.third_place}</span>
                  </div>
                </div>

                {/* 4th Place */}
                <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3.5 text-center">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Fourth Place (4th)
                  </div>
                  <div className="text-base font-bold text-slate-200 mt-1 flex items-center justify-center space-x-2">
                    {getFlagUrl(singleSim.fourth_place) && (
                      <img
                        src={getFlagUrl(singleSim.fourth_place)}
                        alt={singleSim.fourth_place}
                        className="w-5 h-3.5 rounded object-cover"
                      />
                    )}
                    <span>{singleSim.fourth_place}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Knockout Bracket Rounds */}
          {singleSim?.knockout_matches && (
            <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-6">
              <h3 className="text-lg font-bold text-white tracking-tight flex items-center space-x-2">
                <Trophy className="w-5 h-5 text-amber-400" />
                <span>Knockout Elimination Rounds</span>
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Round of 16 */}
                <div className="space-y-3">
                  <div className="text-xs font-bold uppercase tracking-wider text-slate-400 pb-1 border-b border-slate-800">
                    Round of 16 (8 Matches)
                  </div>
                  {singleSim.knockout_matches.round_of_16?.map((m, idx) => (
                    <MatchCard key={idx} match={m} />
                  ))}
                </div>

                {/* Quarter Finals */}
                <div className="space-y-3">
                  <div className="text-xs font-bold uppercase tracking-wider text-slate-400 pb-1 border-b border-slate-800">
                    Quarter-Finals (4 Matches)
                  </div>
                  {singleSim.knockout_matches.quarter_finals?.map((m, idx) => (
                    <MatchCard key={idx} match={m} />
                  ))}
                </div>

                {/* Semi Finals */}
                <div className="space-y-3">
                  <div className="text-xs font-bold uppercase tracking-wider text-slate-400 pb-1 border-b border-slate-800">
                    Semi-Finals (2 Matches)
                  </div>
                  {singleSim.knockout_matches.semi_finals?.map((m, idx) => (
                    <MatchCard key={idx} match={m} />
                  ))}
                </div>

                {/* Finals */}
                <div className="space-y-3">
                  <div className="text-xs font-bold uppercase tracking-wider text-amber-400 pb-1 border-b border-amber-400/30">
                    Grand Final & 3rd Place
                  </div>
                  {singleSim.knockout_matches.final && (
                    <div>
                      <span className="text-[10px] font-extrabold uppercase text-amber-400 block mb-1">
                        🏆 World Cup Final
                      </span>
                      <MatchCard match={singleSim.knockout_matches.final} isGrandFinal />
                    </div>
                  )}
                  {singleSim.knockout_matches.third_place_match && (
                    <div className="mt-4">
                      <span className="text-[10px] font-extrabold uppercase text-slate-400 block mb-1">
                        🥉 Third Place Playoff
                      </span>
                      <MatchCard match={singleSim.knockout_matches.third_place_match} />
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Group Stage Standings */}
          {singleSim?.group_stage && (
            <div className="bg-slate-900/80 rounded-2xl border border-slate-800 p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-white tracking-tight">
                  Group Stage Standings & Qualifiers
                </h3>
                <span className="text-xs text-slate-400">Top 2 in each group advanced to R16</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(singleSim.group_stage).map(([groupKey, data]) => (
                  <div
                    key={groupKey}
                    className="bg-slate-950/70 border border-slate-800/90 rounded-xl p-4 space-y-2.5"
                  >
                    <div className="text-xs font-extrabold text-amber-400 uppercase tracking-wider border-b border-slate-800 pb-1.5 flex items-center justify-between">
                      <span>Group {groupKey}</span>
                      <span className="text-[10px] text-slate-500 font-normal">Final Table</span>
                    </div>

                    <div className="space-y-1.5 text-xs">
                      {data.standings?.map((teamData, idx) => {
                        const isQualifier = idx < 2
                        return (
                          <div
                            key={teamData.team}
                            className={`flex items-center justify-between p-1.5 rounded ${
                              isQualifier ? 'bg-slate-900 text-white font-medium' : 'text-slate-400'
                            }`}
                          >
                            <div className="flex items-center space-x-2 truncate">
                              <span className={`w-3 text-center ${isQualifier ? 'text-amber-400 font-bold' : 'text-slate-600'}`}>
                                {idx + 1}
                              </span>
                              {getFlagUrl(teamData.team) && (
                                <img
                                  src={getFlagUrl(teamData.team)}
                                  alt={teamData.team}
                                  className="w-4 h-3 rounded object-cover"
                                />
                              )}
                              <span className="truncate">{teamData.team}</span>
                            </div>
                            <div className="flex items-center space-x-2 text-[11px] font-mono">
                              <span className="text-slate-500">{teamData.goal_difference > 0 ? `+${teamData.goal_difference}` : teamData.goal_difference}</span>
                              <span className="font-bold text-slate-200">{teamData.points} pts</span>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* VIEW 2: 10,000 MONTE CARLO TOURNAMENT LEADERBOARD */}
      {subView === 'montecarlo' && (
        <div className="space-y-8">
          {/* Chart Header Card */}
          <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl">
            <h3 className="text-lg font-bold text-white tracking-tight mb-1">
              Top 10 Championship Contenders (Monte Carlo Probability)
            </h3>
            <p className="text-xs text-slate-400 mb-6">
              Simulated across 10,000 full tournament draws accounting for match-level variance and penalty shootouts.
            </p>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topContenders} layout="vertical" margin={{ left: 20, right: 30, top: 10, bottom: 10 }}>
                  <XAxis type="number" unit="%" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    tick={{ fill: '#f1f5f9', fontSize: 12, fontWeight: 500 }}
                    width={90}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
                    formatter={(value) => [`${value}%`, 'Championship Win Probability']}
                  />
                  <Bar dataKey="probability" radius={[0, 6, 6, 0]}>
                    {topContenders.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={index === 0 ? '#f59e0b' : index < 3 ? '#fbbf24' : '#38bdf8'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Full 32-Team Progression Table */}
          <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 shadow-xl">
            <h3 className="text-lg font-bold text-white tracking-tight mb-4">
              All 32 Teams Tournament Progression Breakdown
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                    <th className="pb-3 text-center w-8">#</th>
                    <th className="pb-3">Team</th>
                    <th className="pb-3 text-right text-amber-400 font-bold">Win World Cup</th>
                    <th className="pb-3 text-right">Reach Final</th>
                    <th className="pb-3 text-right">Semi-Final</th>
                    <th className="pb-3 text-right">Quarter-Final</th>
                    <th className="pb-3 text-right">Round of 16</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-medium">
                  {leaderboard?.map((item, idx) => (
                    <tr key={item.team} className="hover:bg-slate-800/40 transition">
                      <td className="py-2.5 text-center text-slate-500 font-mono">{idx + 1}</td>
                      <td className="py-2.5 text-white flex items-center space-x-2">
                        {getFlagUrl(item.team) && (
                          <img
                            src={getFlagUrl(item.team)}
                            alt={item.team}
                            className="w-4 h-3 rounded object-cover"
                          />
                        )}
                        <span className="font-semibold">{item.team}</span>
                      </td>
                      <td className="py-2.5 text-right font-bold text-amber-400">
                        {item.win_pct}%
                      </td>
                      <td className="py-2.5 text-right text-slate-200">
                        {item.final_pct}%
                      </td>
                      <td className="py-2.5 text-right text-slate-300">
                        {item.semi_pct}%
                      </td>
                      <td className="py-2.5 text-right text-slate-400">
                        {item.qf_pct}%
                      </td>
                      <td className="py-2.5 text-right text-slate-500">
                        {item.r16_pct}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function MatchCard({ match, isGrandFinal = false }) {
  if (!match) return null

  const isHomeWinner = match.winner === match.home_team
  const isAwayWinner = match.winner === match.away_team

  return (
    <div
      className={`rounded-xl border p-3 transition shadow-sm ${
        isGrandFinal
          ? 'bg-slate-950 border-amber-500/50 shadow-amber-500/10'
          : 'bg-slate-950/80 border-slate-800/80 hover:border-slate-700'
      }`}
    >
      {/* Home Team */}
      <div className="flex items-center justify-between text-xs py-1">
        <div className="flex items-center space-x-2 truncate">
          {getFlagUrl(match.home_team) && (
            <img
              src={getFlagUrl(match.home_team)}
              alt={match.home_team}
              className="w-4 h-3 rounded object-cover"
            />
          )}
          <span className={isHomeWinner ? 'font-bold text-amber-300 truncate' : 'text-slate-300 truncate'}>
            {match.home_team}
          </span>
        </div>
        {isHomeWinner && <Check className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />}
      </div>

      {/* Away Team */}
      <div className="flex items-center justify-between text-xs py-1 border-t border-slate-850">
        <div className="flex items-center space-x-2 truncate">
          {getFlagUrl(match.away_team) && (
            <img
              src={getFlagUrl(match.away_team)}
              alt={match.away_team}
              className="w-4 h-3 rounded object-cover"
            />
          )}
          <span className={isAwayWinner ? 'font-bold text-amber-300 truncate' : 'text-slate-300 truncate'}>
            {match.away_team}
          </span>
        </div>
        {isAwayWinner && <Check className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />}
      </div>

      {match.decided_by_penalties && (
        <div className="mt-1.5 pt-1 border-t border-slate-800/60 text-[10px] text-amber-400/80 italic text-right">
          Decided by Penalty Shootout
        </div>
      )}
    </div>
  )
}
