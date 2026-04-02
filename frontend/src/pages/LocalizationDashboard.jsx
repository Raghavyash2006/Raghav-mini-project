import { useState } from 'react'
import { localize } from '../services/api'
import TextInputBox from '../components/localization/TextInputBox'
import LanguageSelector from '../components/localization/LanguageSelector'
import ToneSelector from '../components/localization/ToneSelector'
import LocalizeButton from '../components/localization/LocalizeButton'
import OutputDisplayPanel from '../components/localization/OutputDisplayPanel'
import ExplanationPanel from '../components/localization/ExplanationPanel'
import RatingSystem from '../components/localization/RatingSystem'
import Alert from '../components/common/Alert'
import Card from '../components/common/Card'

export default function LocalizationDashboard() {
  const [formData, setFormData] = useState({
    text: '',
    target_language: 'es',
    tone: 'neutral'
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleLocalize = async () => {
    if (!formData.text.trim()) {
      setError('Please enter text to localize')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await localize({
        text: formData.text,
        target_language: formData.target_language,
        tone: formData.tone
      })
      setResult(response)
    } catch (err) {
      setError(err.message || 'Failed to localize content')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setFormData({
      ...formData,
      text: ''
    })
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-slate-50 py-8">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Localization Dashboard</h1>
          <p className="mt-2 text-slate-600">Transform your content with semantic localization</p>
        </div>

        {/* Main Layout */}
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Input Section */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <TextInputBox
                value={formData.text}
                onChange={(text) => setFormData({ ...formData, text })}
                placeholder="Enter text to localize..."
                maxLength={5000}
                rows={8}
              />
            </Card>

            <Card>
              <div className="space-y-4">
                <LanguageSelector
                  value={formData.target_language}
                  onChange={(lang) => setFormData({ ...formData, target_language: lang })}
                  label="Target Language"
                />
                <ToneSelector
                  value={formData.tone}
                  onChange={(tone) => setFormData({ ...formData, tone })}
                  label="Tone"
                />
              </div>
            </Card>

            <div className="flex gap-3">
              <LocalizeButton
                onClick={handleLocalize}
                loading={loading}
                disabled={!formData.text.trim()}
                fullWidth={false}
              />
              <button
                onClick={handleClear}
                className="rounded-lg border border-slate-300 bg-white px-6 py-3 font-medium text-slate-700 transition hover:bg-slate-100"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Output Section */}
          <div className="lg:col-span-2 space-y-6">
            {error && (
              <Alert
                type="error"
                title="Error"
                message={error}
                onClose={() => setError(null)}
              />
            )}

            {result ? (
              <>
                <Card>
                  <OutputDisplayPanel result={result} />
                </Card>

                {result.explanation && (
                  <Card>
                    <ExplanationPanel explanation={result.explanation} />
                  </Card>
                )}

                {result.request_id && (
                  <Card>
                    <RatingSystem
                      requestId={result.request_id}
                      onSubmit={() => console.log('Feedback submitted')}
                    />
                  </Card>
                )}
              </>
            ) : (
              <div className="rounded-xl border-2 border-dashed border-slate-300 p-12 text-center">
                <p className="text-slate-500">
                  Enter text and click "Localize Content" to see results
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
