import React, { useState } from 'react'
import { Card, Space, Button, message } from 'antd'
import ChartEditor from './ChartEditor'

function StyleTest() {
  const [specText, setSpecText] = useState('')
  const [savedCharts, setSavedCharts] = useState([])

  const handleSave = ({ specText, thumbDataUrl }) => {
    const newChart = {
      id: Date.now(),
      specText,
      thumbDataUrl,
      timestamp: new Date().toLocaleString()
    }
    setSavedCharts(prev => [newChart, ...prev])
    message.success('图表已保存到历史记录')
  }

  const handleLoadChart = (chart) => {
    setSpecText(chart.specText)
    message.info('已加载图表配置')
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Vega-Lite 图表样式配置测试</h1>
      <p>这个页面用于测试图表编辑器的样式配置功能，包括颜色、透明度、边框、字体等配置选项。</p>
      
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 图表编辑器 */}
        <Card title="图表编辑器" size="large">
          <ChartEditor 
            specText={specText}
            onChange={setSpecText}
            onSave={handleSave}
          />
        </Card>

        {/* 保存的历史记录 */}
        {savedCharts.length > 0 && (
          <Card title="保存的历史记录" size="large">
            <Space wrap>
              {savedCharts.map(chart => (
                <Card 
                  key={chart.id} 
                  size="small" 
                  style={{ width: 200 }}
                  cover={chart.thumbDataUrl && (
                    <img 
                      alt="图表预览" 
                      src={chart.thumbDataUrl} 
                      style={{ height: 120, objectFit: 'contain' }}
                    />
                  )}
                  actions={[
                    <Button 
                      key="load" 
                      type="link" 
                      size="small"
                      onClick={() => handleLoadChart(chart)}
                    >
                      加载
                    </Button>
                  ]}
                >
                  <Card.Meta 
                    title={`图表 ${chart.id}`}
                    description={chart.timestamp}
                  />
                </Card>
              ))}
            </Space>
          </Card>
        )}
      </Space>
    </div>
  )
}

export default StyleTest
