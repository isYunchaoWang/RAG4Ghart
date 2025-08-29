import { Form, Select, InputNumber, ColorPicker, Space, Divider, Switch, Input } from 'antd'

// 样式配置常量
const MARK_COLORS = [
  { label: '默认', value: '' },
  { label: '蓝色系', value: 'blues' },
  { label: '红色系', value: 'reds' },
  { label: '绿色系', value: 'greens' },
  { label: '橙色系', value: 'oranges' },
  { label: '紫色系', value: 'purples' },
  { label: '灰色系', value: 'greys' },
  { label: '彩虹色', value: 'rainbow' },
  { label: '分类色', value: 'category10' },
  { label: '分类色20', value: 'category20' },
  { label: '光谱色', value: 'spectral' },
  { label: 'RdYlBu', value: 'rdylbu' },
  { label: 'Set1', value: 'set1' },
  { label: 'Set2', value: 'set2' },
  { label: 'Set3', value: 'set3' },
]

const OPACITY_OPTIONS = [
  { label: '0.1', value: 0.1 },
  { label: '0.2', value: 0.2 },
  { label: '0.3', value: 0.3 },
  { label: '0.4', value: 0.4 },
  { label: '0.5', value: 0.5 },
  { label: '0.6', value: 0.6 },
  { label: '0.7', value: 0.7 },
  { label: '0.8', value: 0.8 },
  { label: '0.9', value: 0.9 },
  { label: '1.0', value: 1.0 },
]

const STROKE_WIDTH_OPTIONS = [
  { label: '0', value: 0 },
  { label: '0.5', value: 0.5 },
  { label: '1', value: 1 },
  { label: '1.5', value: 1.5 },
  { label: '2', value: 2 },
  { label: '2.5', value: 2.5 },
  { label: '3', value: 3 },
  { label: '4', value: 4 },
  { label: '5', value: 5 },
]

const FONT_FAMILY_OPTIONS = [
  { label: '默认', value: '' },
  { label: 'Arial', value: 'Arial' },
  { label: 'Helvetica', value: 'Helvetica' },
  { label: 'Times New Roman', value: 'Times New Roman' },
  { label: 'Georgia', value: 'Georgia' },
  { label: 'Verdana', value: 'Verdana' },
  { label: 'Courier New', value: 'Courier New' },
  { label: 'Monaco', value: 'Monaco' },
  { label: 'Menlo', value: 'Menlo' },
  { label: 'Consolas', value: 'Consolas' },
]

const FONT_SIZE_OPTIONS = [
  { label: '8px', value: 8 },
  { label: '10px', value: 10 },
  { label: '12px', value: 12 },
  { label: '14px', value: 14 },
  { label: '16px', value: 16 },
  { label: '18px', value: 18 },
  { label: '20px', value: 20 },
  { label: '24px', value: 24 },
  { label: '28px', value: 28 },
  { label: '32px', value: 32 },
]

const AXIS_POSITION_OPTIONS = [
  { label: '默认', value: '' },
  { label: '顶部', value: 'top' },
  { label: '底部', value: 'bottom' },
  { label: '左侧', value: 'left' },
  { label: '右侧', value: 'right' },
]

const STROKE_DASH_OPTIONS = [
  { label: '实线', value: [] },
  { label: '虚线', value: [5, 5] },
  { label: '点线', value: [2, 2] },
  { label: '点划线', value: [5, 5, 1, 5] },
]

function StyleConfig({ chartType, form }) {
  const isBarChart = ['bar'].includes(chartType)
  const isLineChart = ['line'].includes(chartType)
  const isScatterChart = ['scatter'].includes(chartType)
  const isBubbleChart = ['bubble'].includes(chartType)
  const isPieChart = ['pie'].includes(chartType)

  return (
    <div>
      <div style={{ 
        fontSize: '14px', 
        fontWeight: 500, 
        marginBottom: 12, 
        color: '#262626',
        borderBottom: '1px solid #f0f0f0',
        paddingBottom: 8
      }}>
        样式配置
      </div>
      {/* 基础样式和边框配置 */}
      <div style={{ marginBottom: '12px' }}>
        <div style={{ 
          fontSize: '13px', 
          fontWeight: 'bold', 
          marginBottom: '6px',
          color: '#1890ff'
        }}>
          {/* 基础样式 */}
        </div>
                 <Space size={8} wrap>
           {/* 透明度 */}
           <Form.Item label="透明度" name="opacity" style={{ marginBottom: 0 }}>
             <Select 
               id="opacity"
               options={OPACITY_OPTIONS} 
               style={{ width: 100 }}
               placeholder="1.0"
             />
           </Form.Item>

           {/* 边框配置 */}
           <Form.Item label="边框宽度" name="strokeWidth" style={{ marginBottom: 0 }}>
             <Select 
               id="strokeWidth"
               options={STROKE_WIDTH_OPTIONS} 
               style={{ width: 100 }}
               placeholder="0"
             />
           </Form.Item>

           {/* 线条样式（仅适用于线图） */}
           {isLineChart && (
             <Form.Item label="线条样式" name="strokeDash" style={{ marginBottom: 0 }}>
               <Select 
                 id="strokeDash"
                 options={STROKE_DASH_OPTIONS} 
                 style={{ width: 100 }}
                 placeholder="实线"
               />
             </Form.Item>
           )}
        </Space>
      </div>

      {/* 特定样式和字体配置 */}
      <div style={{ marginBottom: '12px' }}>
        <div style={{ 
          fontSize: '13px', 
          fontWeight: 'bold', 
          marginBottom: '6px',
          color: '#1890ff'
        }}>
          {/* 特定样式和字体 */}
        </div>
        <Space size={8} wrap>
                     {/* 柱状图圆角 */}
           {isBarChart && (
             <Form.Item label="圆角半径" name="cornerRadius" style={{ marginBottom: 0 }}>
               <InputNumber 
                 id="cornerRadius"
                 min={0} 
                 max={20} 
                 style={{ width: 100 }}
                 placeholder="0"
               />
             </Form.Item>
           )}

           {/* 气泡图大小（仅气泡图支持） */}
           {isBubbleChart && (
             <Form.Item label="点大小" name="pointSize" style={{ marginBottom: 0 }}>
               <InputNumber 
                 id="pointSize"
                 min={1} 
                 max={100} 
                 style={{ width: 100 }}
                 placeholder="自动"
               />
             </Form.Item>
           )}

           {/* 线图宽度 */}
           {isLineChart && (
             <Form.Item label="线条宽度" name="lineWidth" style={{ marginBottom: 0 }}>
               <InputNumber 
                 id="lineWidth"
                 min={0.5} 
                 max={10} 
                 step={0.5}
                 style={{ width: 100 }}
                 placeholder="1"
               />
             </Form.Item>
           )}

           {/* 饼图内半径 */}
           {isPieChart && (
             <Form.Item label="内半径" name="innerRadius" style={{ marginBottom: 0 }}>
               <InputNumber 
                 id="innerRadius"
                 min={0} 
                 max={100} 
                 style={{ width: 100 }}
                 placeholder="0"
               />
             </Form.Item>
           )}

           <Form.Item label="字体族" name="fontFamily" style={{ marginBottom: 0 }}>
             <Select 
               id="fontFamily"
               options={FONT_FAMILY_OPTIONS} 
               style={{ width: 120 }}
               placeholder="选择字体"
               allowClear
             />
           </Form.Item>

           <Form.Item label="字体大小" name="fontSize" style={{ marginBottom: 0 }}>
             <Select 
               id="fontSize"
               options={FONT_SIZE_OPTIONS} 
               style={{ width: 100 }}
               placeholder="默认"
               allowClear
             />
           </Form.Item>
        </Space>
      </div>

      {/* 轴和图例配置 */}
      <div style={{ marginBottom: '12px' }}>
        <div style={{ 
          fontSize: '13px', 
          fontWeight: 'bold', 
          marginBottom: '6px',
          color: '#1890ff'
        }}>
          {/* 轴和图例配置 */}
        </div>
                 <Space size={8} wrap>
           <Form.Item label="显示网格" name="showGrid" style={{ marginBottom: 0 }}>
             <Switch id="showGrid" />
           </Form.Item>

           <Form.Item label="显示图例" name="showLegend" style={{ marginBottom: 0 }}>
             <Switch id="showLegend" />
           </Form.Item>

           <Form.Item label="图例位置" name="legendPosition" style={{ marginBottom: 0 }}>
             <Select 
               id="legendPosition"
               options={[
                 { label: '默认', value: '' },
                 { label: '顶部', value: 'top' },
                 { label: '底部', value: 'bottom' },
                 { label: '左侧', value: 'left' },
                 { label: '右侧', value: 'right' },
               ]} 
               style={{ width: 100 }}
               placeholder="默认"
               allowClear
             />
           </Form.Item>

           <Form.Item label="图例方向" name="legendOrientation" style={{ marginBottom: 0 }}>
             <Select 
               id="legendOrientation"
               options={[
                 { label: '默认', value: '' },
                 { label: '水平', value: 'horizontal' },
                 { label: '垂直', value: 'vertical' },
               ]} 
               style={{ width: 100 }}
               placeholder="默认"
               allowClear
             />
           </Form.Item>
         </Space>
      </div>


    </div>
  )
}

export default StyleConfig
