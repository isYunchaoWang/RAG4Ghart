import { Form, Select, InputNumber, ColorPicker, Space, Divider, Switch, Input } from 'antd'

// Style configuration constants
const MARK_COLORS = [
  { label: 'Default', value: '' },
  { label: 'Vibrant Blue', value: '#1890ff' },
  { label: 'Elegant Red', value: '#f5222d' },
  { label: 'Fresh Green', value: '#52c41a' },
  { label: 'Warm Orange', value: '#fa8c16' },
  { label: 'Royal Purple', value: '#722ed1' },
  { label: 'Modern Grey', value: '#8c8c8c' },
  { label: 'Ocean Blue', value: '#13c2c2' },
  { label: 'Sunset Pink', value: '#eb2f96' },
  { label: 'Forest Green', value: '#389e0d' },
  { label: 'Golden Yellow', value: '#fadb14' },
  { label: 'Deep Indigo', value: '#2f54eb' },
  { label: 'Coral Red', value: '#ff7875' },
  { label: 'Mint Green', value: '#36cfc9' },
  { label: 'Lavender', value: '#b37feb' },
  { label: 'Peach', value: '#ffa940' },
]

// 预定义的颜色方案
const COLOR_SCHEMES = [
  { label: 'Default', value: '' },
  { label: 'Modern Blue', value: 'modern-blue' },
  { label: 'Warm Sunset', value: 'warm-sunset' },
  { label: 'Ocean Breeze', value: 'ocean-breeze' },
  { label: 'Forest Green', value: 'forest-green' },
  { label: 'Royal Purple', value: 'royal-purple' },
  { label: 'Vibrant Rainbow', value: 'vibrant-rainbow' },
  { label: 'Pastel Dream', value: 'pastel-dream' },
  { label: 'Monochrome', value: 'monochrome' },
  { label: 'Fire & Ice', value: 'fire-ice' },
]

// 颜色方案定义
export const COLOR_SCHEME_DEFINITIONS = {
  'modern-blue': ['#1890ff', '#40a9ff', '#69c0ff', '#91d5ff', '#bae7ff'],
  'warm-sunset': ['#fa8c16', '#ffa940', '#ffc069', '#ffd591', '#ffe7ba'],
  'ocean-breeze': ['#13c2c2', '#36cfc9', '#5cdbd3', '#87e8de', '#b5f5ec'],
  'forest-green': ['#52c41a', '#73d13d', '#95de64', '#b7eb8f', '#d9f7be'],
  'royal-purple': ['#722ed1', '#9254de', '#b37feb', '#d3adf7', '#efdbff'],
  'vibrant-rainbow': ['#f5222d', '#fa8c16', '#fadb14', '#52c41a', '#13c2c2', '#1890ff', '#722ed1', '#eb2f96'],
  'pastel-dream': ['#ffb3ba', '#ffdfba', '#ffffba', '#baffc9', '#bae1ff', '#e6b3ff'],
  'monochrome': ['#000000', '#333333', '#666666', '#999999', '#cccccc'],
  'fire-ice': ['#ff4d4f', '#ff7875', '#ffa39e', '#87e8de', '#5cdbd3', '#13c2c2'],
}

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
  { label: 'Default', value: '' },
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
  { label: 'Default', value: '' },
  { label: 'Top', value: 'top' },
  { label: 'Bottom', value: 'bottom' },
  { label: 'Left', value: 'left' },
  { label: 'Right', value: 'right' },
]

const STROKE_DASH_OPTIONS = [
  { label: 'Solid', value: [] },
  { label: 'Dashed', value: [5, 5] },
  { label: 'Dotted', value: [2, 2] },
  { label: 'Dash-Dot', value: [5, 5, 1, 5] },
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
        Style Configuration
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
           <Form.Item label="Opacity" name="opacity" style={{ marginBottom: 0 }}>
             <Select 
               id="opacity"
               options={OPACITY_OPTIONS} 
               style={{ width: 100 }}
               placeholder="1.0"
             />
           </Form.Item>

           {/* 边框配置 */}
           <Form.Item label="Border Width" name="strokeWidth" style={{ marginBottom: 0 }}>
             <Select 
               id="strokeWidth"
               options={STROKE_WIDTH_OPTIONS} 
               style={{ width: 100 }}
               placeholder="0"
             />
           </Form.Item>

           {/* 线条样式（仅适用于线图） */}
           {isLineChart && (
             <Form.Item label="Line Style" name="strokeDash" style={{ marginBottom: 0 }}>
               <Select 
                 id="strokeDash"
                 options={STROKE_DASH_OPTIONS} 
                 style={{ width: 100 }}
                 placeholder="Solid"
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
             <Form.Item label="Corner Radius" name="cornerRadius" style={{ marginBottom: 0 }}>
               <InputNumber 
                 id="cornerRadius"
                 min={0} 
                 max={20} 
                 style={{ width: 100 }}
                 placeholder="0"
               />
             </Form.Item>
           )}

           {/* 散点图和气泡图大小 */}
           {(isScatterChart || isBubbleChart) && (
             <Form.Item label="Point Size" name="pointSize" style={{ marginBottom: 0 }}>
               <InputNumber 
                 id="pointSize"
                 min={1} 
                 max={100} 
                 style={{ width: 100 }}
                 placeholder="Auto"
               />
             </Form.Item>
           )}

           {/* 线图宽度 */}
           {isLineChart && (
             <Form.Item label="Line Width" name="lineWidth" style={{ marginBottom: 0 }}>
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
             <Form.Item label="Inner Radius" name="innerRadius" style={{ marginBottom: 0 }}>
               <InputNumber 
                 id="innerRadius"
                 min={0} 
                 max={100} 
                 style={{ width: 100 }}
                 placeholder="0"
               />
             </Form.Item>
           )}

           <Form.Item label="Font Family" name="fontFamily" style={{ marginBottom: 0 }}>
             <Select 
               id="fontFamily"
               options={FONT_FAMILY_OPTIONS} 
               style={{ width: 120 }}
               placeholder="Select Font"
               allowClear
             />
           </Form.Item>

           <Form.Item label="Font Size" name="fontSize" style={{ marginBottom: 0 }}>
             <Select 
               id="fontSize"
               options={FONT_SIZE_OPTIONS} 
               style={{ width: 100 }}
               placeholder="Default"
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
           <Form.Item label="Show Grid" name="showGrid" style={{ marginBottom: 0 }}>
             <Switch id="showGrid" />
           </Form.Item>

           <Form.Item label="Show Legend" name="showLegend" style={{ marginBottom: 0 }}>
             <Switch id="showLegend" />
           </Form.Item>

           <Form.Item label="Legend Position" name="legendPosition" style={{ marginBottom: 0 }}>
             <Select 
               id="legendPosition"
               options={[
                 { label: 'Default', value: '' },
                 { label: 'Top', value: 'top' },
                 { label: 'Bottom', value: 'bottom' },
                 { label: 'Left', value: 'left' },
                 { label: 'Right', value: 'right' },
               ]} 
               style={{ width: 100 }}
               placeholder="Default"
               allowClear
             />
           </Form.Item>

           <Form.Item label="Legend Orientation" name="legendOrientation" style={{ marginBottom: 0 }}>
             <Select 
               id="legendOrientation"
               options={[
                 { label: 'Default', value: '' },
                 { label: 'Horizontal', value: 'horizontal' },
                 { label: 'Vertical', value: 'vertical' },
               ]} 
               style={{ width: 100 }}
               placeholder="Default"
               allowClear
             />
           </Form.Item>
         </Space>
      </div>


    </div>
  )
}

export default StyleConfig
