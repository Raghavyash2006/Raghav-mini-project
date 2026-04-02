export default function OutputPreview({ result }) {
  if (!result) return null
  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">Localized output</h2>
      <p className="mt-2 whitespace-pre-wrap">{result.localized_text}</p>
      <p className="mt-3 text-sm text-slate-500">Source: {result.source_language} → Target: {result.target_language}</p>
    </div>
  )
}
