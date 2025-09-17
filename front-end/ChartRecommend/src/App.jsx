import './App.css'
import { theme } from 'antd'
import LeftPanel from './components/LeftPanel'
import ChartEditor from './components/ChartEditor'
import { useState, useEffect, useRef } from 'react'

function App() {
  const { token } = theme.useToken()

  const [specText, setSpecText] = useState('')
  const [history, setHistory] = useState([])
  const [selectedChartType, setSelectedChartType] = useState('')
  const leftPanelRef = useRef(null)
  const chartEditorRef = useRef(null)

  const STORAGE_KEY = 'chartHistory'

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      console.log('Loading from localStorage:', {
        key: STORAGE_KEY,
        raw: raw,
        rawLength: raw ? raw.length : 0
      })
      if (raw) {
        const parsed = JSON.parse(raw)
        console.log('Parsed from localStorage:', {
          isArray: Array.isArray(parsed),
          length: Array.isArray(parsed) ? parsed.length : 0,
          parsed: parsed
        })
        if (Array.isArray(parsed)) {
          const withTs = parsed.map((it, idx) => ({
            ...it,
            ts: typeof it.ts === 'number' ? it.ts : (new Date(it.time).getTime() || idx),
            thumb: it.thumb || it.thumbDataUrl || '',
            specText: it.specText || it.text || '',
          }))
          withTs.sort((a, b) => a.ts - b.ts)
          console.log('Final history loaded:', withTs)
          setHistory(withTs)
        } else {
          console.warn('localStorage数据不是数组格式，无法加载历史记录')
        }
      } else {
        console.log('localStorage中没有找到数据')
      }
    } catch (error) {
      console.error('Error loading from localStorage:', error)
      console.error('请检查localStorage中的数据格式是否正确')
    }
  }, [])

  useEffect(() => {
    try {
      console.log('Saving to localStorage:', {
        key: STORAGE_KEY,
        historyLength: history.length,
        history: history
      })
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
    } catch (error) {
      console.error('Error saving to localStorage:', error)
    }
  }, [history])

  const addHistory = (payload) => {
    // Compatible with both string and object parameters
    const isObj = payload && typeof payload === 'object'
    const text = isObj ? payload.specText : (payload || '')
    const thumb = isObj ? (payload.thumbDataUrl || payload.thumb || '') : ''
    const trimmed = (text || '').trim()
    if (!trimmed) {
      console.log('No text to save, skipping')
      return
    }
    
    const now = new Date()
    const record = {
      title: tryGetTitle(trimmed),
      time: now.toLocaleString(),
      ts: now.getTime(),
      specText: trimmed,
      thumb,
    }
    
    console.log('Adding to history:', {
      currentHistoryLength: history.length,
      newRecord: record,
      payload
    })
    
    setHistory((prev) => {
      const newHistory = [...prev, record]
      console.log('New history length:', newHistory.length)
      return newHistory
    })
  }

  const tryGetTitle = (text) => {
    try {
      const obj = JSON.parse(text)
      return obj?.description || obj?.title || 'Untitled Chart'
    } catch {
      return 'Untitled Chart'
    }
  }

  const onSelectHistory = (item) => {
    setSpecText(item.specText || item.text || '')
  }

  const onClearHistory = () => {
    setHistory([])
    try { localStorage.removeItem(STORAGE_KEY) } catch {}
  }
  // 在App组件的useEffect中添加
  useEffect(() => {
    window.leftPanelRef = leftPanelRef
    window.chartEditorRef = chartEditorRef
  }, [])

  // 手动刷新localStorage数据
  const refreshFromLocalStorage = () => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      console.log('手动刷新localStorage:', {
        key: STORAGE_KEY,
        raw: raw,
        rawLength: raw ? raw.length : 0
      })
      if (raw) {
        const parsed = JSON.parse(raw)
        console.log('手动刷新解析结果:', {
          isArray: Array.isArray(parsed),
          length: Array.isArray(parsed) ? parsed.length : 0,
          parsed: parsed
        })
        if (Array.isArray(parsed)) {
          const withTs = parsed.map((it, idx) => ({
            ...it,
            ts: typeof it.ts === 'number' ? it.ts : (new Date(it.time).getTime() || idx),
            thumb: it.thumb || it.thumbDataUrl || '',
            specText: it.specText || it.text || '',
          }))
          withTs.sort((a, b) => a.ts - b.ts)
          console.log('手动刷新最终结果:', withTs)
          setHistory(withTs)
        } else {
          console.warn('localStorage数据不是数组格式，无法加载历史记录')
        }
      } else {
        console.log('localStorage中没有找到数据')
      }
    } catch (error) {
      console.error('手动刷新localStorage时出错:', error)
    }
  }

  const onDeleteHistory = (index) => {
    setHistory((prev) => {
      const newHistory = prev.filter((_, i) => i !== index)
      return newHistory
    })
  }

  const onReorderHistory = (startIndex, endIndex) => {
    setHistory((prev) => {
      const newHistory = [...prev]
      const [removed] = newHistory.splice(startIndex, 1)
      newHistory.splice(endIndex, 0, removed)
      return newHistory
    })
  }

  const onChartSelect = (chartType) => {
    setSelectedChartType(chartType)
    // Clear specText to let ChartEditor reinitialize
    setSpecText('')
  }

  return (
    <div className="app-root" style={{ background: token.colorBgBase, height: '100vh', display: 'flex' }}>
      <div className="app-left" style={{ padding: 16, flex: 7, minWidth: 0 }}>
        <LeftPanel ref={leftPanelRef} historyItems={history} onSelectHistory={onSelectHistory} onClearHistory={onClearHistory} onDeleteHistory={onDeleteHistory} onReorderHistory={onReorderHistory} onChartSelect={onChartSelect} onRefreshHistory={refreshFromLocalStorage} />
      </div>

      <div className="app-right" style={{ padding: 16, background: token.colorBgContainer, display: 'flex', flexDirection: 'column', gap: 12, flex: 3, minWidth: 0, minHeight: 0 }}>
        <div style={{ flex: 6, minHeight: 0 }}>
          <ChartEditor ref={chartEditorRef} specText={specText} onChange={setSpecText} onSave={addHistory} selectedChartType={selectedChartType} />
        </div>
      </div>
    </div>
  )
}

export default App
