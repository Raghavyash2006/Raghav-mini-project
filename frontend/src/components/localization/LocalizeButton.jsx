import { Zap } from 'lucide-react'
import LoadingSpinner from '../common/LoadingSpinner'

export default function LocalizeButton({ 
  onClick, 
  loading = false, 
  disabled = false,
  fullWidth = true 
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-3 font-medium text-white shadow-lg transition-all hover:shadow-xl hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed ${fullWidth ? 'w-full' : ''}`}
    >
      {loading ? (
        <>
          <LoadingSpinner size="sm" />
          Localizing...
        </>
      ) : (
        <>
          <Zap className="h-4 w-4" />
          Localize Content
        </>
      )}
    </button>
  )
}
