import { useState } from 'react'
import { Star } from 'lucide-react'
import { submitFeedback } from '../../services/api'
import Alert from '../common/Alert'

export default function RatingSystem({ requestId, onSubmit }) {
  const [rating, setRating] = useState(0)
  const [hoveredRating, setHoveredRating] = useState(0)
  const [comment, setComment] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async () => {
    if (rating === 0) {
      setError('Please select a rating')
      return
    }

    setLoading(true)
    setError(null)

    try {
      await submitFeedback({
        request_id: requestId,
        rating,
        comment: comment || undefined
      })
      setSubmitted(true)
      setTimeout(() => {
        setRating(0)
        setComment('')
        setSubmitted(false)
      }, 3000)
      onSubmit?.()
    } catch (err) {
      setError(err.message || 'Failed to submit feedback')
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <Alert 
        type="success" 
        title="Thanks for your feedback!" 
        message="Your rating helps us improve the localization quality."
      />
    )
  }

  return (
    <div className="rounded-lg border border-slate-300 bg-white p-4">
      <h4 className="mb-3 font-semibold text-slate-900">Rate this localization</h4>

      {error && <Alert type="error" message={error} className="mb-3" />}

      {/* Star Rating */}
      <div className="mb-4 flex gap-2">
        {[1, 2, 3, 4, 5].map(star => (
          <button
            key={star}
            onClick={() => setRating(star)}
            onMouseEnter={() => setHoveredRating(star)}
            onMouseLeave={() => setHoveredRating(0)}
            className="transition-transform hover:scale-110"
          >
            <Star
              className={`h-6 w-6 ${
                star <= (hoveredRating || rating)
                  ? 'fill-amber-400 text-amber-400'
                  : 'text-slate-300'
              }`}
            />
          </button>
        ))}
      </div>

      {/* Comment Input */}
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Optional: Share your feedback (max 500 characters)"
        maxLength={500}
        rows={3}
        className="mb-3 w-full rounded-lg border border-slate-300 p-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
      />

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={loading || rating === 0}
        className="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        {loading ? 'Submitting...' : 'Submit Feedback'}
      </button>
    </div>
  )
}
