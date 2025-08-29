import { Input, Typography, theme } from 'antd'
import ChartHistory from './ChartHistory'

const { TextArea } = Input
const { Title } = Typography

function LeftPanel({ historyItems = [], onSelectHistory, onClearHistory, onDeleteHistory }) {
  const { token } = theme.useToken()
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, height: '100%' }}>
      <div className="app-left-top">
        <Title level={5} style={{ marginBottom: 8 }}>文本输入</Title>
        <TextArea
          placeholder="在这里输入文本..."
          autoSize={{ minRows: 3, maxRows: 6 }}
          style={{ height: '100%' }}
        />
      </div>
      <div className="app-left-bottom" style={{ border: `1px solid ${token.colorBorderSecondary}`, borderRadius: 8, padding: 12 }}>
        <Title level={5} style={{ marginTop: 0 }}>信息展示区</Title>
      </div>
      <div className="app-left-history" style={{ border: `1px solid ${token.colorBorderSecondary}`, borderRadius: 8, padding: 12, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        <Title level={5} style={{ marginTop: 0 }}>历史记录</Title>
        <div style={{ flex: 1, minHeight: 0 }}>
          <ChartHistory items={historyItems} onSelect={onSelectHistory} onClear={onClearHistory} onDelete={onDeleteHistory} />
        </div>
      </div>
    </div>
  )
}

export default LeftPanel 