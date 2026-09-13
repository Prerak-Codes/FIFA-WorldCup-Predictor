import React from 'react'
import { Trophy, Swords, BarChart3, Activity } from 'lucide-react'

export default function Navbar({ activeTab, setActiveTab, apiStatus }) {
  const navItems = [
    { id: 'predictor', label: 'Match Predictor', icon: Swords },
    { id: 'simulator', label: 'Tournament Bracket & Monte Carlo', icon: Trophy },
    { id: 'analytics', label: 'Team Analytics & Elo', icon: BarChart3 },
  ]

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-slate-950/80 border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-amber-400 to-yellow-200 flex items-center justify-center shadow-lg shadow-amber-500/20">
              <Trophy className="w-5 h-5 text-slate-950 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg text-white tracking-tight">FIFA World Cup 2026</span>
                <span className="px-1.5 py-0.5 text-[10px] font-extrabold uppercase rounded bg-amber-400/10 text-amber-400 border border-amber-400/30">
                  AI Predictor
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Powered by XGBoost Machine Learning & Monte Carlo Simulation
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = activeTab === item.id
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer ${
                    isActive
                      ? 'bg-slate-800 text-white shadow-sm border border-slate-700'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              )
            })}
          </nav>

          {/* System API Status */}
          <div className="flex items-center space-x-2 text-xs">
            <div
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full border ${
                apiStatus === 'online'
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  : apiStatus === 'checking'
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  apiStatus === 'online'
                    ? 'bg-emerald-400 animate-pulse'
                    : apiStatus === 'checking'
                    ? 'bg-amber-400 animate-ping'
                    : 'bg-rose-400'
                }`}
              />
              <span className="font-semibold capitalize">
                {apiStatus === 'online' ? 'API Online' : apiStatus === 'checking' ? 'Connecting...' : 'API Offline'}
              </span>
            </div>
          </div>
        </div>

        {/* Mobile Nav Tabs */}
        <div className="flex md:hidden space-x-1 py-2 border-t border-slate-800/60 overflow-x-auto">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = activeTab === item.id
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap ${
                  isActive
                    ? 'bg-slate-800 text-white border border-slate-700'
                    : 'text-slate-400 hover:bg-slate-900'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-amber-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            )
          })}
        </div>
      </div>
    </header>
  )
}
