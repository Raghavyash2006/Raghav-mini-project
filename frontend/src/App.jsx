import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/common/Navbar'
import HomePage from './pages/HomePage'
import LocalizationDashboard from './pages/LocalizationDashboard'
import HistoryPage from './pages/HistoryPage'
import AnalyticsDashboard from './pages/AnalyticsDashboard'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<LocalizationDashboard />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/analytics" element={<AnalyticsDashboard />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
