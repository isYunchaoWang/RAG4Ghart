import { Form, Input, Select, Space, InputNumber, Divider } from 'antd'

const FIELD_TYPES = [
  { label: '定量 quantitative', value: 'quantitative' },
  { label: '类别 nominal', value: 'nominal' },
  { label: '顺序 ordinal', value: 'ordinal' },
  { label: '时间 temporal', value: 'temporal' },
]

const COLOR_TYPES = [
  { label: '连续 quantitative', value: 'quantitative' },
  { label: '分类型 nominal', value: 'nominal' },
]

const AGG_FUNCS = [
  { label: '无', value: '' },
  { label: 'sum', value: 'sum' },
  { label: 'mean', value: 'mean' },
  { label: 'median', value: 'median' },
  { label: 'min', value: 'min' },
  { label: 'max', value: 'max' },
  { label: 'count', value: 'count' },
]

// 定义每种图表类型的配置需求
const CHART_CONFIGS = {
  bar: {
    fields: ['x', 'y', 'color'],
    defaultTypes: { x: 'ordinal', y: 'quantitative', color: 'nominal' },
    defaultFields: { x: 'x', y: 'y', color: '' },
    showAggregate: false,
    showSize: false,
    description: '柱状图用于比较不同类别的数值'
  },
  
  line: {
    fields: ['x', 'y', 'color'],
    defaultTypes: { x: 'ordinal', y: 'quantitative', color: 'nominal' },
    defaultFields: { x: 'x', y: 'y', color: '' },
    showAggregate: false,
    showSize: false,
    description: '折线图用于显示数据随时间或有序类别的变化趋势'
  },
  
  scatter: {
    fields: ['x', 'y', 'color'],
    defaultTypes: { x: 'quantitative', y: 'quantitative', color: 'nominal' },
    defaultFields: { x: 'x', y: 'y', color: '' },
    showAggregate: false,
    showSize: false,
    description: '散点图用于显示两个连续变量之间的相关关系'
  },
  
  bubble: {
    fields: ['x', 'y', 'color', 'size'],
    defaultTypes: { x: 'quantitative', y: 'quantitative', color: 'nominal', size: 'quantitative' },
    defaultFields: { x: 'x', y: 'y', color: '', size: 'size' },
    showAggregate: false,
    showSize: true,
    description: '气泡图通过气泡大小展示第三个维度的数据'
  },
  
  pie: {
    fields: ['category', 'value'],
    defaultTypes: { category: 'nominal', value: 'quantitative' },
    defaultFields: { category: 'category', value: 'value' },
    showAggregate: false,
    showSize: false,
    description: '饼图用于显示各部分占整体的比例关系'
  },
  
  heatmap: {
    fields: ['x', 'y', 'value'],
    defaultTypes: { x: 'ordinal', y: 'ordinal', value: 'quantitative' },
    defaultFields: { x: 'x', y: 'y', value: 'value' },
    showAggregate: false,
    showSize: false,
    description: '热力图用颜色深浅表示数值大小的矩阵图'
  },
  
  treemap: {
    fields: ['category', 'size', 'color'],
    defaultTypes: { category: 'nominal', size: 'quantitative', color: 'nominal' },
    defaultFields: { category: 'category', size: 'size', color: 'category' },
    showAggregate: false,
    showSize: true,
    description: '树状图用嵌套矩形表示层次数据'
  },
  
  // 暂不支持的复杂图表类型，使用默认配置
  chord: {
    fields: ['x', 'y'],
    defaultTypes: { x: 'ordinal', y: 'quantitative' },
    defaultFields: { x: 'x', y: 'y' },
    showAggregate: false,
    showSize: false,
    description: '弦乐图（暂未完全支持，显示为柱状图）'
  },
  
  funnel: {
    fields: ['x', 'y'],
    defaultTypes: { x: 'ordinal', y: 'quantitative' },
    defaultFields: { x: 'x', y: 'y' },
    showAggregate: false,
    showSize: false,
    description: '漏斗图（暂未完全支持，显示为柱状图）'
  },
  
  node_link: {
    fields: ['x', 'y'],
    defaultTypes: { x: 'ordinal', y: 'quantitative' },
    defaultFields: { x: 'x', y: 'y' },
    showAggregate: false,
    showSize: false,
    description: '节点链接图（暂未完全支持，显示为柱状图）'
  }
}

function ChartConfig({ chartType, form, onFieldChange }) {
  const config = CHART_CONFIGS[chartType] || CHART_CONFIGS.bar
  
  // 获取字段标签
  const getFieldLabel = (field) => {
    const labels = {
      x: 'X轴字段',
      y: 'Y轴字段', 
      color: '颜色字段',
      size: '大小字段',
      category: '分类字段',
      value: '数值字段',
      group: '分组字段',
      dimension: '维度字段',
      parent: '父级字段',
      source: '源字段',
      target: '目标字段'
    }
    return labels[field] || field
  }
  
  // 获取字段占位符
  const getFieldPlaceholder = (field) => {
    const placeholders = {
      x: '例如：category',
      y: '例如：value', 
      color: '例如：type',
      size: '例如：size',
      category: '例如：category',
      value: '例如：value',
      group: '例如：group',
      dimension: '例如：dimension',
      parent: '例如：parent',
      source: '例如：source',
      target: '例如：target'
    }
    return placeholders[field] || `例如：${field}`
  }

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
        字段配置
      </div>
      {/* 动态字段配置 */}
      <div style={{ marginBottom: '16px' }}>
        <Space size={12} wrap>
        {config.fields.map(field => (
          <div key={field} style={{ display: 'flex', gap: '8px', alignItems: 'end' }}>
            <Form.Item 
              label={getFieldLabel(field)} 
              name={`${field}Field`}
              style={{ minWidth: 160, marginBottom: 0 }}
            >
              <Input 
                id={`${field}Field`}
                placeholder={getFieldPlaceholder(field)} 
              />
            </Form.Item>
            
            <Form.Item 
              label="类型" 
              name={`${field}Type`}
              style={{ minWidth: 140, marginBottom: 0 }}
            >
              <Select 
                id={`${field}Type`}
                options={field === 'color' && chartType === 'heatmap' ? COLOR_TYPES : FIELD_TYPES}
                placeholder="选择类型"
              />
            </Form.Item>
          </div>
        ))}
        </Space>
      </div>

      {/* 聚合函数 */}
      {config.showAggregate && (
        <>
          <Divider style={{ margin: '16px 0 12px 0' }} />
          <Form.Item label="聚合函数" name="aggregate" style={{ marginBottom: 0 }}>
            <Select 
              id="aggregate"
              options={AGG_FUNCS} 
              style={{ width: 160 }} 
              placeholder="选择聚合函数"
            />
          </Form.Item>
        </>
      )}
    </div>
  )
}

export default ChartConfig