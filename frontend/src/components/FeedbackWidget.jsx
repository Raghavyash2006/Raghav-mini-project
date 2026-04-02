import { useState } from 'react'
import { submitFeedback } from '../services/api'

export default function FeedbackWidget({ requestId }) {
  const [rating, setRating] = useState(5)
  const [comment, setComment] = useState('')
  const [status, setStatus] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus('submitting')
    try {
      await submitFeedback({ request_id: requestId, rating, comment })
      setStatus('submitted')
    } catch (err) {
      setStatus('error')
    }
  }

  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm mt-4">
      <h3 className="font-semibold">Feedback</h3>
      <form onSubmit={handleSubmit} className="mt-2 space-y-2">
        <div>
          <label className="block text-sm">Rating (1-5)</label>
          <input type="number" min="1" max="5" value={rating} onChange={(e) => setRating(Number(e.target.value))} className="mt-1 w-24 rounded-lg border p-2" />
        </div>
        <div>
          <label className="block text-sm">Comment</label>
          <textarea value={comment} onChange={(e) => setComment(e.target.value)} className="mt-1 w-full rounded-lg border p-2" rows={3}></textarea>
        </div>
        <button className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700" disabled={status==='submitting'}>Submit</button>
      </form>
      {status === 'submitted' && <p className="text-green-700">Thank you for your feedback!</p>}
      {status === 'error' && <p className="text-red-700">Failed to send feedback.</p>}
    </div>
  )
}
