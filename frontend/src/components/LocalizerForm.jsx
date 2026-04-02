import { useState } from 'react'
import { localize } from '../services/api'

export default function LocalizerForm({ onResult }) {
  const [sourceText, setSourceText] = useState('')
  const [sourceLanguage, setSourceLanguage] = useState('en')
  const [targetLanguage, setTargetLanguage] = useState('es')
  const [audience, setAudience] = useState('general')
  const [tone, setTone] = useState('friendly')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const result = await localize({
        source_text: sourceText,
        source_language: sourceLanguage,
        target_language: targetLanguage,
        audience,
        tone,
      })
      onResult(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <div>
        <label className="block text-sm font-medium">Source text</label>
        <textarea
          value={sourceText}
          onChange={(e) => setSourceText(e.target.value)}
          rows={6}
          className="mt-1 w-full rounded-lg border p-2"
          required
        />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium">Source language</label>
          <input value={sourceLanguage} onChange={(e) => setSourceLanguage(e.target.value)} className="mt-1 w-full rounded-lg border p-2" />
        </div>
        <div>
          <label className="block text-sm font-medium">Target language</label>
          <input value={targetLanguage} onChange={(e) => setTargetLanguage(e.target.value)} className="mt-1 w-full rounded-lg border p-2" />
        </div>
        <div>
          <label className="block text-sm font-medium">Audience</label>
          <input value={audience} onChange={(e) => setAudience(e.target.value)} className="mt-1 w-full rounded-lg border p-2" />
        </div>
        <div>
          <label className="block text-sm font-medium">Tone</label>
          <input value={tone} onChange={(e) => setTone(e.target.value)} className="mt-1 w-full rounded-lg border p-2" />
        </div>
      </div>

      <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700" disabled={loading}>
        {loading ? 'Localizing...' : 'Localize Content'}
      </button>
      {error && <p className="text-red-600">{error}</p>}
    </form>
  )
}
