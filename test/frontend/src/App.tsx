import { useState } from 'react'
import './index.css'
import UploadZone from './components/UploadZone'
import ResultViewer from './components/ResultViewer'
import SettingsModal from './components/SettingsModal'

function App() {
  const [currentStep, setCurrentStep] = useState<'upload' | 'grading' | 'result'>('upload')
  const [result, setResult] = useState<any>(null)
  const [showSettings, setShowSettings] = useState(false)

  const handleUploadComplete = async (file: File) => {
    setCurrentStep('grading')
    const formData = new FormData()
    formData.append('file', file)

    try {
      // 1. Upload
      const uploadRes = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      })
      const uploadData = await uploadRes.json()

      // 2. Grade
      const gradeRes = await fetch('http://localhost:8000/api/grade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename: uploadData.filename }),
      })
      const gradeData = await gradeRes.json()

      setResult(gradeData)
      setCurrentStep('result')
    } catch (error) {
      console.error(error)
      alert("处理失败，请重试")
      setCurrentStep('upload')
    }
  }

  return (
    <>
      {/* Settings Button */}
      <button
        className="settings-button"
        onClick={() => setShowSettings(true)}
        title="LLM API 配置"
      >
        ⚙️
      </button>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />

      <div className="container" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: '4rem' }}>
        <header style={{ marginBottom: '3rem', textAlign: 'center' }}>
          <h1 style={{ fontSize: '3rem', background: 'linear-gradient(to right, #818cf8, #c084fc)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', marginBottom: '1rem' }}>
            智能试卷批改系统
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }}>
            上传试卷照片，AI 自动批改并生成报告
          </p>
        </header>

        <main style={{ width: '100%', maxWidth: '800px' }}>
          {currentStep === 'upload' && (
            <div className="animate-fade-in">
              <UploadZone onFileSelect={handleUploadComplete} />
            </div>
          )}

          {currentStep === 'grading' && (
            <div className="glass-panel animate-fade-in" style={{ padding: '3rem', textAlign: 'center' }}>
              <div className="loader" style={{ marginBottom: '1rem' }}>Processing...</div>
              <h2 style={{ fontSize: '1.5rem' }}>正在智能批改中...</h2>
              <p style={{ color: 'var(--text-muted)' }}>识别文字 • 语义分析 • 生成报告</p>
            </div>
          )}

          {currentStep === 'result' && result && (
            <div className="animate-fade-in">
              <ResultViewer result={result} onReset={() => setCurrentStep('upload')} />
            </div>
          )}
        </main>
      </div>
    </>
  )
}

export default App
