export default function ExplanationPanel({ explanation }) {
  if (!explanation) return null

  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
      <h4 className="mb-2 font-semibold text-amber-900">Localization Details</h4>
      <p className="text-sm text-amber-800 leading-relaxed">
        {explanation}
      </p>
    </div>
  )
}
