import { Link } from 'react-router-dom'
import { Globe, Home, History, BarChart3, Zap } from 'lucide-react'

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 font-bold text-lg">
            <div className="rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 p-2">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <span className="hidden sm:inline text-slate-900">LocalizeAI</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-1 sm:gap-2">
            <Link
              to="/"
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 transition-colors"
            >
              <Home className="h-4 w-4" />
              <span className="hidden sm:inline">Home</span>
            </Link>
            <Link
              to="/dashboard"
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 transition-colors"
            >
              <Globe className="h-4 w-4" />
              <span className="hidden sm:inline">Localize</span>
            </Link>
            <Link
              to="/history"
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 transition-colors"
            >
              <History className="h-4 w-4" />
              <span className="hidden sm:inline">History</span>
            </Link>
            <Link
              to="/analytics"
              className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 transition-colors"
            >
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Analytics</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
