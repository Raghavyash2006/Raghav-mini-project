import { AlertCircle, CheckCircle, XCircle, Info } from 'lucide-react'

export default function Alert({ type = 'info', title, message, onClose }) {
  const styles = {
    info: {
      container: 'bg-blue-50 border-blue-200',
      icon: 'text-blue-600',
      title: 'text-blue-900',
      message: 'text-blue-700'
    },
    success: {
      container: 'bg-green-50 border-green-200',
      icon: 'text-green-600',
      title: 'text-green-900',
      message: 'text-green-700'
    },
    error: {
      container: 'bg-red-50 border-red-200',
      icon: 'text-red-600',
      title: 'text-red-900',
      message: 'text-red-700'
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200',
      icon: 'text-yellow-600',
      title: 'text-yellow-900',
      message: 'text-yellow-700'
    }
  }

  const style = styles[type] || styles.info
  const Icons = { info: Info, success: CheckCircle, error: XCircle, warning: AlertCircle }
  const Icon = Icons[type] || Info

  return (
    <div className={`rounded-lg border p-4 ${style.container}`}>
      <div className="flex gap-3">
        <Icon className={`h-5 w-5 flex-shrink-0 ${style.icon}`} />
        <div className="flex-1">
          {title && <h3 className={`font-medium ${style.title}`}>{title}</h3>}
          {message && <p className={`mt-1 text-sm ${style.message}`}>{message}</p>}
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  )
}
