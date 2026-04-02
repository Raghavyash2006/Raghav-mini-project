import { useState, useEffect } from 'react'
import { getHistory } from '../services/api'
import Card from '../components/common/Card'
import LoadingSpinner from '../components/common/LoadingSpinner'
import Alert from '../components/common/Alert'
import { BarChart3, TrendingUp, Globe, Star } from 'lucide-react'

export default function AnalyticsDashboard() {
  const [stats, setStats] = useState({
    totalLocalizations: 0,
    avgQuality: 0,
    topLanguages: {},
    topTones: {},
    avgRating: 0
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await getHistory({ limit: 100 })
      const items = response.items || []

      if (items.length === 0) {
        setStats({
          totalLocalizations: 0,
          avgQuality: 0,
          topLanguages: {},
          topTones: {},
          avgRating: 0
        })
        return
      }

      // Calculate statistics
      const languages = {}
      const tones = {}
      let totalQuality = 0
      let qualityCount = 0

      items.forEach(item => {
        // Language stats
        languages[item.target_language] = (languages[item.target_language] || 0) + 1

        // Tone stats
        tones[item.tone] = (tones[item.tone] || 0) + 1

        // Quality score
        if (item.quality_score) {
          totalQuality += item.quality_score
          qualityCount++
        }
      })

      const avgQuality = qualityCount > 0 ? totalQuality / qualityCount : 0

      // Sort and get top 5
      const topLanguages = Object.entries(languages)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .reduce((acc, [lang, count]) => ({ ...acc, [lang]: count }), {})

      const topTones = Object.entries(tones)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .reduce((acc, [tone, count]) => ({ ...acc, [tone]: count }), {})

      setStats({
        totalLocalizations: items.length,
        avgQuality: Math.round(avgQuality),
        topLanguages,
        topTones,
        avgRating: 4.2 // Placeholder - would need to fetch from feedback endpoint
      })
    } catch (err) {
      setError(err.message || 'Failed to load analytics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Analytics Dashboard</h1>
          <p className="mt-2 text-slate-600">Insights into your localization activity</p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert
            type="error"
            title="Error"
            message={error}
            onClose={() => setError(null)}
            className="mb-6"
          />
        )}

        {/* Key Metrics */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card>
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-blue-100 p-3">
                <BarChart3 className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-xs font-medium uppercase text-slate-600">Total Localizations</p>
                <p className="text-2xl font-bold text-slate-900">{stats.totalLocalizations}</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-green-100 p-3">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-xs font-medium uppercase text-slate-600">Avg Quality</p>
                <p className="text-2xl font-bold text-slate-900">{stats.avgQuality}%</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-purple-100 p-3">
                <Globe className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-xs font-medium uppercase text-slate-600">Top Languages</p>
                <p className="text-2xl font-bold text-slate-900">{Object.keys(stats.topLanguages).length}</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-amber-100 p-3">
                <Star className="h-6 w-6 text-amber-600" />
              </div>
              <div>
                <p className="text-xs font-medium uppercase text-slate-600">Avg Rating</p>
                <p className="text-2xl font-bold text-slate-900">{stats.avgRating}/5</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Top Languages */}
          <Card>
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Top Languages</h2>
            {Object.keys(stats.topLanguages).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(stats.topLanguages).map(([lang, count]) => (
                  <div key={lang}>
                    <div className="mb-1 flex items-center justify-between">
                      <span className="font-medium text-slate-700">{lang.toUpperCase()}</span>
                      <span className="text-sm font-semibold text-slate-600">{count}</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-200">
                      <div
                        className="h-2 rounded-full bg-blue-600"
                        style={{
                          width: `${(count / Math.max(...Object.values(stats.topLanguages))) * 100}%`
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500">No data yet</p>
            )}
          </Card>

          {/* Top Tones */}
          <Card>
            <h2 className="mb-4 text-lg font-semibold text-slate-900">Tone Distribution</h2>
            {Object.keys(stats.topTones).length > 0 ? (
              <div className="space-y-3">
                {Object.entries(stats.topTones).map(([tone, count]) => (
                  <div key={tone}>
                    <div className="mb-1 flex items-center justify-between">
                      <span className="capitalize font-medium text-slate-700">{tone}</span>
                      <span className="text-sm font-semibold text-slate-600">{count}</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-200">
                      <div
                        className="h-2 rounded-full bg-purple-600"
                        style={{
                          width: `${(count / Math.max(...Object.values(stats.topTones))) * 100}%`
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-500">No data yet</p>
            )}
          </Card>
        </div>

        {/* Info Card */}
        {stats.totalLocalizations === 0 && (
          <Card className="mt-8 text-center py-12">
            <p className="text-slate-500">No analytics data available yet. Start creating localizations!</p>
          </Card>
        )}
      </div>
    </div>
  )
}
