import { Typography, Button, Space } from 'antd'

const { Text } = Typography

function ChartHistory({ items, onSelect, onClear }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Space style={{ marginBottom: 8, justifyContent: 'space-between' }} align="center">
        <Text strong>历史记录</Text>
        <Button size="small" onClick={onClear}>清空</Button>
      </Space>
      <div style={{ flex: 1, overflowX: 'auto', overflowY: 'hidden' }}>
        <div style={{ display: 'flex', gap: 8 }}>
          {Array.isArray(items) && items.length > 0 ? (
            items.map((item, index) => (
              <div key={index} style={{ border: '1px solid #f0f0f0', borderRadius: 6, padding: 8, cursor: 'pointer', minWidth: 160, display: 'flex', flexDirection: 'column', alignItems: 'center' }} onClick={() => onSelect(item, index)}>
                {item.thumb ? (
                  <img src={item.thumb} alt={item.title || `记录 ${index + 1}`} style={{ width: 140, height: 100, objectFit: 'contain', background: '#fafafa', borderRadius: 4, marginBottom: 6 }} />
                ) : (
                  <div style={{ width: 140, height: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fafafa', borderRadius: 4, marginBottom: 6 }}>
                    <Text type="secondary">无预览</Text>
                  </div>
                )}
                <div style={{ fontWeight: 500, maxWidth: 140, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.title || `记录 ${index + 1}`}</div>
                <div style={{ color: '#999', maxWidth: 140, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.time}</div>
              </div>
            ))
          ) : (
            <div style={{ color: '#999' }}>暂无历史</div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ChartHistory 