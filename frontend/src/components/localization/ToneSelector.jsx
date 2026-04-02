import { ChevronDown } from 'lucide-react'

const tones = [
  { value: 'formal', label: 'Formal', description: 'Professional and structured' },
  { value: 'casual', label: 'Casual', description: 'Friendly and relaxed' },
  { value: 'marketing', label: 'Marketing', description: 'Persuasive and engaging' },
  { value: 'technical', label: 'Technical', description: 'Precise and accurate' },
  { value: 'neutral', label: 'Neutral', description: 'Objective and balanced' }
]

export default function ToneSelector({ value, onChange, label = 'Tone' }) {
  const selectedTone = tones.find(t => t.value === value)

  return (
    <div className="flex flex-col">
      <label className="mb-2 text-sm font-medium text-slate-700">{label}</label>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full appearance-none rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-slate-900 transition-colors hover:border-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        >
          {tones.map(tone => (
            <option key={tone.value} value={tone.value}>
              {tone.label}
            </option>
          ))}
        </select>
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
      </div>
      {selectedTone && (
        <p className="mt-1 text-xs text-slate-500">{selectedTone.description}</p>
      )}
    </div>
  )
}
