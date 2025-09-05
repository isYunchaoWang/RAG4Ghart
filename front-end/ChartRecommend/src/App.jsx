import './App.css'
import { theme } from 'antd'
import LeftPanel from './components/LeftPanel'
import ChartEditor from './components/ChartEditor'
import { useState, useEffect } from 'react'

function App() {
  const { token } = theme.useToken()

  const [specText, setSpecText] = useState('')
  const [history, setHistory] = useState([])
  const [selectedChartType, setSelectedChartType] = useState('')

  const STORAGE_KEY = 'chartHistory'

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) {
        const parsed = JSON.parse(raw)
        if (Array.isArray(parsed)) {
          const withTs = parsed.map((it, idx) => ({
            ...it,
            ts: typeof it.ts === 'number' ? it.ts : (new Date(it.time).getTime() || idx),
            thumb: it.thumb || it.thumbDataUrl || '',
            specText: it.specText || it.text || '',
          }))
          withTs.sort((a, b) => a.ts - b.ts)
          setHistory(withTs)
        }
      }
    } catch {}
  }, [])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
    } catch {}
  }, [history])

  const addHistory = (payload) => {
    // 兼容字符串与对象两种入参
    const isObj = payload && typeof payload === 'object'
    const text = isObj ? payload.specText : (payload || '')
    const thumb = isObj ? (payload.thumbDataUrl || payload.thumb || '') : ''
    const trimmed = (text || '').trim()
    if (!trimmed) return
    const now = new Date()
    const record = {
      title: tryGetTitle(trimmed),
      time: now.toLocaleString(),
      ts: now.getTime(),
      specText: trimmed,
      thumb,
    }
    setHistory((prev) => [...prev, record])
  }

  const tryGetTitle = (text) => {
    try {
      const obj = JSON.parse(text)
      return obj?.description || obj?.title || '未命名图表'
    } catch {
      return '未命名图表'
    }
  }

  const onSelectHistory = (item) => {
    setSpecText(item.specText || item.text || '')
  }

  const onClearHistory = () => {
    setHistory([])
    try { localStorage.removeItem(STORAGE_KEY) } catch {}
  }

  const onDeleteHistory = (index) => {
    setHistory((prev) => {
      const newHistory = prev.filter((_, i) => i !== index)
      return newHistory
    })
  }

  const onChartSelect = (chartType) => {
    setSelectedChartType(chartType)
    // 清空specText，让ChartEditor重新初始化
    setSpecText('')
  }

  return (
    <div className="app-root" style={{ background: token.colorBgBase, height: '100vh', display: 'flex' }}>
      <div className="app-left" style={{ padding: 16, flex: 7, minWidth: 0 }}>
        <LeftPanel historyItems={history} onSelectHistory={onSelectHistory} onClearHistory={onClearHistory} onDeleteHistory={onDeleteHistory} onChartSelect={onChartSelect} />
      </div>

      <div className="app-right" style={{ padding: 16, background: token.colorBgContainer, display: 'flex', flexDirection: 'column', gap: 12, flex: 3, minWidth: 0, minHeight: 0 }}>
        <div style={{ flex: 6, minHeight: 0 }}>
          <ChartEditor specText={specText} onChange={setSpecText} onSave={addHistory} selectedChartType={selectedChartType} />
        </div>
      </div>
    </div>
  )
}

export default App
