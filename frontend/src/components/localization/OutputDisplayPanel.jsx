import { Copy, CheckCircle } from 'lucide-react'
import { useState } from 'react'
import Badge from '../common/Badge'

export default function OutputDisplayPanel({ 
  result,
  onCopy = true 
}) {
  const [copied, setCopied] = useState(false)

  if (!result) return null

  const handleCopy = () => {
    navigator.clipboard.writeText(result.localized_text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">Localized Output</h3>
        <div className="flex gap-2">
          <Badge variant="blue">{result.tone_applied || 'neutral'}</Badge>
          <Badge variant="purple">{result.sentiment_preserved || 'neutral'}</Badge>
          {result.quality_score && (
            <Badge variant="green">{Math.round(result.quality_score)}% quality</Badge>
          )}
        </div>
      </div>

      {/* Output Text */}
      <div className="relative rounded-lg border border-slate-300 bg-gradient-to-br from-slate-50 to-slate-100 p-4">
        <p className="whitespace-pre-wrap font-mono text-slate-900 text-base leading-relaxed">
          {result.localized_text}
        </p>
        {onCopy && (
          <button
            onClick={handleCopy}
            className="absolute right-3 top-3 rounded-lg bg-white p-2 shadow-sm hover:shadow-md transition-all"
            title="Copy to clipboard"
          >
            {copied ? (
              <CheckCircle className="h-4 w-4 text-green-600" />
            ) : (
              <Copy className="h-4 w-4 text-slate-600" />
            )}
          </button>
        )}
      </div>

      {/* Detected Language */}
      {result.detected_language && (
        <div className="rounded-lg bg-blue-50 p-3 border border-blue-200">
          <p className="text-xs font-medium text-blue-600">
            Detected source language: <span className="font-semibold">{result.detected_language.toUpperCase()}</span>
          </p>
        </div>
      )}

      {/* Cultural Adaptations */}
      {result.cultural_adaptations && result.cultural_adaptations.length > 0 && (
        <div className="rounded-lg bg-purple-50 p-3 border border-purple-200">
          <p className="text-xs font-semibold text-purple-900 mb-2">Cultural Adaptations:</p>
          <ul className="space-y-1">
            {result.cultural_adaptations.map((adaptation, idx) => (
              <li key={idx} className="text-xs text-purple-700">
                • {adaptation}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
