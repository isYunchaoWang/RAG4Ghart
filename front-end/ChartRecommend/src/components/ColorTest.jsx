import React, { useState } from 'react'
import { Card, Space, Button, message, Divider } from 'antd'
import ChartEditor from './ChartEditor'

function ColorTest() {
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
      <h1>Vega-Lite 图表颜色配置测试</h1>
      <p>这个页面用于测试图表编辑器的颜色配置功能，验证颜色设置是否正确应用到图表元素上。</p>

      <Divider />

      <div style={{ marginBottom: '20px', padding: '16px', background: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: '6px' }}>
        <h3>测试说明：</h3>
        <ul>
          <li><strong>图表颜色</strong>：用于设置单色图表的颜色（如柱状图的柱子颜色）</li>
          <li><strong>颜色方案</strong>：用于设置分类数据的颜色方案（当有color字段时）</li>
          <li>选择柱状图，设置图表颜色，观察柱子颜色变化</li>
          <li>选择堆叠柱状图，设置颜色方案，观察不同分类的颜色</li>
        </ul>
      </div>

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

export default ColorTest
