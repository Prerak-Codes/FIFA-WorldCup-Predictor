import React, { useState } from 'react'
import { ArrowLeftRight, CheckCircle2, AlertTriangle, Shield, TrendingUp, Zap, HelpCircle } from 'lucide-react'
import { getFlagUrl } from '../utils/teams'

export default function PredictorTab({ teams, onPredict, prediction, loading, error }) {
  const [homeTeam, setHomeTeam] = useState('Spain')
  const [awayTeam, setAwayTeam] = useState('England')
  const [neutralVenue, setNeutralVenue] = useState(true)

  const handleSwap = () => {
    const temp = homeTeam
    setHomeTeam(awayTeam)
    setAwayTeam(temp)
  }

  const handleCalculate = (e) => {
    e.preventDefault()
    if (homeTeam === awayTeam) return
    onPredict(homeTeam, awayTeam, neutralVenue)
  }

  const homeFlag = getFlagUrl(homeTeam)
  const awayFlag = getFlagUrl(awayTeam)

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Head-to-head Selector Panel */}
      <div className="bg-slate-900/90 rounded-2xl border border-slate-800 p-6 md:p-8 shadow-xl relative overflow-hidden">
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -left-16 -bottom-16 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="text-center max-w-xl mx-auto mb-6">
          <h2 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
            Head-to-Head Match Forecast
          </h2>
          <p className="text-sm text-slate-400 mt-1">
            Predict outcomes for any 2026 World Cup match using our multi-feature calibrated XGBoost model.
          </p>
        </div>

        <form onSubmit={handleCalculate} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-11 gap-4 items-center">
            {/* Team A (Home) */}
            <div className="md:col-span-5 bg-slate-950/60 rounded-xl p-5 border border-slate-800/80 hover:border-slate-700 transition">
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Team A {neutralVenue ? '(Nominal Home)' : '(Home)'}
              </label>
              <div className="flex items-center space-x-3">
                {homeFlag ? (
                  <img
                    src={homeFlag}
                    alt={homeTeam}
                    className="w-10 h-7 object-cover rounded shadow-sm border border-slate-700"
                  />
                ) : (
                  <div className="w-10 h-7 rounded bg-slate-800 flex items-center justify-center text-xs">⚽</div>
                )}
                <select
                  value={homeTeam}
                  onChange={(e) => setHomeTeam(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white font-medium focus:outline-none focus:ring-2 focus:ring-amber-400/50"
                >
                  {teams.map((t) => (
                    <option key={t} value={t} disabled={t === awayTeam}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Swap & VS Badge */}
            <div className="md:col-span-1 flex flex-col items-center justify-center">
              <button
                type="button"
                onClick={handleSwap}
                title="Swap Teams"
                className="w-10 h-10 rounded-full bg-slate-800 hover:bg-slate-700 border border-slate-700 flex items-center justify-center text-slate-300 hover:text-amber-400 transition shadow-md"
              >
                <ArrowLeftRight className="w-4 h-4" />
              </button>
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest mt-1">VS</span>
            </div>

            {/* Team B (Away) */}
            <div className="md:col-span-5 bg-slate-950/60 rounded-xl p-5 border border-slate-800/80 hover:border-slate-700 transition">
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                Team B {neutralVenue ? '(Nominal Away)' : '(Away)'}
              </label>
              <div className="flex items-center space-x-3">
                {awayFlag ? (
                  <img
                    src={awayFlag}
                    alt={awayTeam}
                    className="w-10 h-7 object-cover rounded shadow-sm border border-slate-700"
                  />
                ) : (
                  <div className="w-10 h-7 rounded bg-slate-800 flex items-center justify-center text-xs">⚽</div>
                )}
                <select
                  value={awayTeam}
                  onChange={(e) => setAwayTeam(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white font-medium focus:outline-none focus:ring-2 focus:ring-amber-400/50"
                >
                  {teams.map((t) => (
                    <option key={t} value={t} disabled={t === homeTeam}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Venue & Action Controls */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 border-t border-slate-800/80">
            <label className="flex items-center space-x-2 text-sm text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={neutralVenue}
                onChange={(e) => setNeutralVenue(e.target.checked)}
                className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-amber-500 focus:ring-amber-400"
              />
              <span>World Cup Neutral Venue Match (recommended)</span>
            </label>

            <button
              type="submit"
              disabled={loading || homeTeam === awayTeam}
              className="w-full sm:w-auto px-8 py-3 rounded-xl font-bold text-slate-950 bg-gradient-to-r from-amber-400 to-yellow-300 hover:from-amber-300 hover:to-yellow-200 shadow-lg shadow-amber-500/20 transition-all transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 cursor-pointer"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                  <span>Computing Prediction...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 fill-current" />
                  <span>Calculate Match Forecast</span>
                </>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Prediction Output Results */}
      {prediction && (
        <div className="space-y-6">
          {/* Verdict Banner */}
          <div className="bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 rounded-2xl border border-amber-500/30 p-6 shadow-xl relative overflow-hidden">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center space-x-1.5 mb-1">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Model Projection Verdict</span>
                </span>
                <h3 className="text-2xl md:text-3xl font-extrabold text-white">
                  {prediction.outcome_verdict}
                </h3>
                <p className="text-sm text-slate-400 mt-1">
                  Estimated goal difference:{' '}
                  <span className="font-semibold text-slate-200">
                    {prediction.projected_goal_difference > 0 ? '+' : ''}
                    {prediction.projected_goal_difference} goals
                  </span>
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <div className="bg-slate-800/80 border border-slate-700/80 px-4 py-2 rounded-xl text-center">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Model Confidence</div>
                  <div className="text-lg font-bold text-amber-300 capitalize">{prediction.confidence_level}</div>
                </div>
              </div>
            </div>
          </div>

          {/* 3-Card Probability Meters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Home Win Card */}
            <div className="bg-slate-900/90 rounded-xl border border-emerald-500/30 p-5 shadow-lg relative overflow-hidden">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                  {prediction.home_team} Win
                </span>
                <span className="text-xs text-slate-400">Home</span>
              </div>
              <div className="text-3xl font-extrabold text-white mb-3">
                {prediction.probabilities.home_win_pct}%
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-emerald-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, Math.max(0, prediction.probabilities.home_win_pct))}%` }}
                />
              </div>
            </div>

            {/* Draw Card */}
            <div className="bg-slate-900/90 rounded-xl border border-slate-700/60 p-5 shadow-lg relative overflow-hidden">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  Draw Outcome
                </span>
                <span className="text-xs text-slate-400">Extra Time Possible</span>
              </div>
              <div className="text-3xl font-extrabold text-white mb-3">
                {prediction.probabilities.draw_pct}%
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-slate-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, Math.max(0, prediction.probabilities.draw_pct))}%` }}
                />
              </div>
            </div>

            {/* Away Win Card */}
            <div className="bg-slate-900/90 rounded-xl border border-rose-500/30 p-5 shadow-lg relative overflow-hidden">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-rose-400">
                  {prediction.away_team} Win
                </span>
                <span className="text-xs text-slate-400">Away</span>
              </div>
              <div className="text-3xl font-extrabold text-white mb-3">
                {prediction.probabilities.away_win_pct}%
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-rose-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, Math.max(0, prediction.probabilities.away_win_pct))}%` }}
                />
              </div>
            </div>
          </div>

          {/* Head-to-Head Metrics Table */}
          <div className="bg-slate-900/90 rounded-xl border border-slate-800 p-6 shadow-lg">
            <h4 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-4 flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-amber-400" />
              <span>Head-to-Head Tactical Feature Comparison</span>
            </h4>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <th className="pb-3 text-emerald-400">{prediction.home_team}</th>
                    <th className="pb-3 text-center text-slate-400">Feature Metric</th>
                    <th className="pb-3 text-right text-rose-400">{prediction.away_team}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-medium">
                  <tr>
                    <td className="py-3 text-white font-bold">{prediction.home_metrics.elo_rating}</td>
                    <td className="py-3 text-center text-slate-400">Current Elo Rating</td>
                    <td className="py-3 text-right text-white font-bold">{prediction.away_metrics.elo_rating}</td>
                  </tr>
                  <tr>
                    <td className="py-3 text-slate-200">#{prediction.home_metrics.fifa_rank}</td>
                    <td className="py-3 text-center text-slate-400">FIFA World Ranking</td>
                    <td className="py-3 text-right text-slate-200">#{prediction.away_metrics.fifa_rank}</td>
                  </tr>
                  <tr>
                    <td className="py-3 text-slate-200">{prediction.home_metrics.win_rate_pct}%</td>
                    <td className="py-3 text-center text-slate-400">Historical Win Rate</td>
                    <td className="py-3 text-right text-slate-200">{prediction.away_metrics.win_rate_pct}%</td>
                  </tr>
                  <tr>
                    <td className="py-3 text-slate-200">{prediction.home_metrics.goals_scored_per_match}</td>
                    <td className="py-3 text-center text-slate-400">Goals Scored / Match</td>
                    <td className="py-3 text-right text-slate-200">{prediction.away_metrics.goals_scored_per_match}</td>
                  </tr>
                  <tr>
                    <td className="py-3 text-slate-200">{prediction.home_metrics.goals_conceded_per_match}</td>
                    <td className="py-3 text-center text-slate-400">Goals Conceded / Match</td>
                    <td className="py-3 text-right text-slate-200">{prediction.away_metrics.goals_conceded_per_match}</td>
                  </tr>
                  <tr>
                    <td className="py-3 text-slate-200">{prediction.home_metrics.clean_sheet_pct}%</td>
                    <td className="py-3 text-center text-slate-400">Clean Sheet %</td>
                    <td className="py-3 text-right text-slate-200">{prediction.away_metrics.clean_sheet_pct}%</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Historical Encounters Note */}
            {prediction.h2h_matches_played !== undefined && (
              <div className="mt-4 pt-4 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
                <span>
                  Historical head-to-head encounters on record:{' '}
                  <strong className="text-white">{prediction.h2h_matches_played} matches</strong>
                </span>
                <span>
                  {prediction.home_team} {prediction.h2h_home_wins || 0}W - {prediction.h2h_draws || 0}D -{' '}
                  {prediction.h2h_away_wins || 0}W {prediction.away_team}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
