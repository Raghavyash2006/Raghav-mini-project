export default function Card({ children, className = '' }) {
  return (
    <div className={`rounded-xl border border-slate-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow ${className}`}>
      {children}
    </div>
  )
}
