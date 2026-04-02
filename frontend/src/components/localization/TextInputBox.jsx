export default function TextInputBox({ 
  value, 
  onChange, 
  placeholder = 'Enter text to localize...', 
  maxLength = 5000,
  rows = 6
}) {
  const charCount = value.length
  const isNearLimit = charCount > maxLength * 0.9

  return (
    <div className="flex flex-col">
      <label className="mb-2 text-sm font-medium text-slate-700">Source Text</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        maxLength={maxLength}
        rows={rows}
        className="w-full resize-none rounded-lg border border-slate-300 bg-white p-4 font-mono text-sm text-slate-900 placeholder-slate-400 transition-colors hover:border-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
      />
      <div className="mt-2 flex items-center justify-between">
        <p className="text-xs text-slate-500">
          {value.split('\n').length} lines • {value.split(/\s+/).filter(Boolean).length} words
        </p>
        <p className={`text-xs font-medium ${isNearLimit ? 'text-amber-600' : 'text-slate-500'}`}>
          {charCount} / {maxLength}
        </p>
      </div>
    </div>
  )
}
