import { Link } from 'react-router-dom'
import { Zap, Globe, Sparkles, TrendingUp, ArrowRight } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Hero Section */}
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="mb-6 inline-block rounded-full bg-white p-3 shadow-lg">
            <Zap className="h-8 w-8 text-blue-600" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl md:text-6xl">
            Localization Beyond Translation
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600">
            AI-powered content localization with cultural context, tone adaptation, and semantic meaning preservation.
          </p>
          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Link
              to="/dashboard"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-8 py-3 font-semibold text-white hover:bg-blue-700 transition-colors shadow-lg"
            >
              Get Started <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/history"
              className="inline-flex items-center justify-center gap-2 rounded-lg border-2 border-blue-600 px-8 py-3 font-semibold text-blue-600 hover:bg-blue-50 transition-colors"
            >
              View History
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-20 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {[
            {
              icon: Sparkles,
              title: 'Semantic Translation',
              description: 'Translates meaning, not words. Idioms adapt culturally.'
            },
            {
              icon: Globe,
              title: 'Cultural Adaptation',
              description: 'Context-aware localization for target audiences.'
            },
            {
              icon: Zap,
              title: 'Tone Preservation',
              description: 'Maintain your message tone across all languages.'
            },
            {
              icon: TrendingUp,
              title: 'Analytics',
              description: 'Track localization quality and feedback trends.'
            },
            {
              icon: Globe,
              title: '12+ Languages',
              description: 'Support for major languages worldwide.'
            },
            {
              icon: Sparkles,
              title: 'Instant Results',
              description: 'Real-time semantic localization powered by AI.'
            }
          ].map((feature, idx) => {
            const Icon = feature.icon
            return (
              <div key={idx} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
                <Icon className="h-8 w-8 text-blue-600 mb-3" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">{feature.title}</h3>
                <p className="text-slate-600">{feature.description}</p>
              </div>
            )
          })}
        </div>

        {/* Example Section */}
        <div className="mt-20 rounded-2xl border border-slate-200 bg-white p-8 shadow-lg">
          <h2 className="mb-6 text-2xl font-bold text-slate-900">How It Works</h2>
          <div className="grid gap-6 sm:grid-cols-2">
            <div>
              <h3 className="mb-2 font-semibold text-slate-900">Input</h3>
              <p className="rounded-lg bg-slate-100 p-4 font-mono text-sm text-slate-700">
                "It's raining cats and dogs"
              </p>
            </div>
            <div>
              <h3 className="mb-2 font-semibold text-slate-900">Output (Hindi)</h3>
              <p className="rounded-lg bg-blue-100 p-4 font-mono text-sm text-blue-700">
                "बहुत तेज बारिश हो रही है"
              </p>
              <p className="mt-2 text-xs text-slate-500">
                ✓ Semantic meaning preserved, not literal translation
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
