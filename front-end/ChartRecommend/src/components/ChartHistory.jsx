import { Typography, Button, Space, Popconfirm } from 'antd'
import { DeleteOutlined } from '@ant-design/icons'

const { Text } = Typography

function ChartHistory({ items, onSelect, onClear, onDelete }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', position: 'relative' }}>
      {/* Clear button - top right corner */}
      <Button 
        size="small" 
        onClick={onClear}
        style={{
          position: 'absolute',
          top: 0,
          right: 0,
          zIndex: 2
        }}
      >
        Clear
      </Button>
      <div style={{ flex: 1, overflowX: 'auto', overflowY: 'hidden' }}>
        <div style={{ display: 'flex', gap: 8 }}>
          {Array.isArray(items) && items.length > 0 ? (
            items.map((item, index) => (
              <div key={index} style={{ border: '1px solid #f0f0f0', borderRadius: 6, padding: 8, minWidth: 160, display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
                {/* Delete button */}
                <Popconfirm
                  title="Are you sure you want to delete this record?"
                  onConfirm={(e) => {
                    e.stopPropagation()
                    onDelete(index)
                  }}
                  onCancel={(e) => e.stopPropagation()}
                  okText="Confirm"
                  cancelText="Cancel"
                >
                  <Button
                    type="text"
                    size="small"
                    icon={<DeleteOutlined />}
                    style={{
                      position: 'absolute',
                      top: 4,
                      right: 4,
                      zIndex: 1,
                      color: '#ff4d4f',
                      background: 'rgba(255, 255, 255, 0.9)',
                      border: 'none',
                      borderRadius: '50%',
                      width: 24,
                      height: 24,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                    onClick={(e) => e.stopPropagation()}
                  />
                </Popconfirm>
                
                {/* Chart content */}
                <div 
                  style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}
                  onClick={() => onSelect(item, index)}
                >
                  {item.thumb ? (
                    <img src={item.thumb} alt={item.title || `Record ${index + 1}`} style={{ width: 140, height: 100, objectFit: 'contain', background: '#fafafa', borderRadius: 4, marginBottom: 6 }} />
                  ) : (
                    <div style={{ width: 140, height: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fafafa', borderRadius: 4, marginBottom: 6 }}>
                      <Text type="secondary">No Preview</Text>
                    </div>
                  )}
                  <div style={{ fontWeight: 500, maxWidth: 140, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.title || `记录 ${index + 1}`}</div>
                  <div style={{ color: '#999', maxWidth: 140, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.time}</div>
                </div>
              </div>
            ))
          ) : (
            <div style={{ color: '#999' }}>No history</div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ChartHistory 