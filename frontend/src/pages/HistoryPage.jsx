import { useState, useEffect } from 'react'
import { getHistory } from '../services/api'
import Card from '../components/common/Card'
import LoadingSpinner from '../components/common/LoadingSpinner'
import Alert from '../components/common/Alert'
import Badge from '../components/common/Badge'
import { ChevronLeft, ChevronRight, Copy } from 'lucide-react'

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [filterLanguage, setFilterLanguage] = useState('')

  useEffect(() => {
    fetchHistory()
  }, [page, filterLanguage])

  const fetchHistory = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await getHistory({
        page,
        limit: 10,
        ...(filterLanguage && { target_language: filterLanguage })
      })
      setHistory(response.items || [])
      setTotalPages(Math.ceil(response.total / response.page_size))
    } catch (err) {
      setError(err.message || 'Failed to fetch history')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text)
  }

  const languages = [...new Set(history.map(item => item.target_language))]

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Localization History</h1>
          <p className="mt-2 text-slate-600">View and manage your past localizations</p>
        </div>

        {/* Filters and Controls */}
        <Card className="mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className="mb-2 block text-sm font-medium text-slate-700">Filter by Language</label>
              <select
                value={filterLanguage}
                onChange={(e) => {
                  setFilterLanguage(e.target.value)
                  setPage(1)
                }}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              >
                <option value="">All Languages</option>
                {languages.map(lang => (
                  <option key={lang} value={lang}>
                    {lang.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={fetchHistory}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
              >
                Refresh
              </button>
            </div>
          </div>
        </Card>

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

        {/* Loading State */}
        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : history.length === 0 ? (
          <Card className="text-center py-12">
            <p className="text-slate-500">No localization history yet. Start by creating your first localization.</p>
          </Card>
        ) : (
          <>
            {/* History List */}
            <div className="space-y-4">
              {history.map((item) => (
                <Card key={item.id} className="hover:shadow-md">
                  <div className="space-y-3">
                    {/* Badges */}
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="blue">{item.target_language.toUpperCase()}</Badge>
                      <Badge variant="purple">{item.tone}</Badge>
                      <Badge variant={item.sentiment === 'positive' ? 'green' : item.sentiment === 'negative' ? 'amber' : 'default'}>
                        {item.sentiment}
                      </Badge>
                      {item.quality_score && (
                        <Badge variant="green">{Math.round(item.quality_score)}%</Badge>
                      )}
                    </div>

                    {/* Original and Localized Text */}
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div>
                        <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Original</p>
                        <p className="line-clamp-3 text-sm text-slate-700 bg-slate-50 p-2 rounded">
                          {item.original_text}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Localized</p>
                        <div className="relative group">
                          <p className="line-clamp-3 text-sm text-slate-700 bg-blue-50 p-2 rounded">
                            {item.localized_text}
                          </p>
                          <button
                            onClick={() => handleCopy(item.localized_text)}
                            className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-white rounded"
                            title="Copy"
                          >
                            <Copy className="h-4 w-4 text-slate-600" />
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Explanation */}
                    {item.explanation && (
                      <div className="text-xs text-slate-600 bg-amber-50 p-2 rounded border border-amber-200">
                        <span className="font-semibold">Details: </span>{item.explanation}
                      </div>
                    )}

                    {/* Date */}
                    <p className="text-xs text-slate-500">
                      {new Date(item.created_at).toLocaleString()}
                    </p>
                  </div>
                </Card>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="rounded-lg border border-slate-300 p-2 hover:bg-slate-100 disabled:opacity-50"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <span className="text-sm text-slate-600">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="rounded-lg border border-slate-300 p-2 hover:bg-slate-100 disabled:opacity-50"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
