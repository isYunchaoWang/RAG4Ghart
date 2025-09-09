import { Form, Input, Select, Space, InputNumber, Divider } from 'antd'

const FIELD_TYPES = [
  { label: 'Quantitative', value: 'quantitative' },
  { label: 'Nominal', value: 'nominal' },
  { label: 'Ordinal', value: 'ordinal' },
  { label: 'Temporal', value: 'temporal' },
]

const COLOR_TYPES = [
  { label: 'Quantitative', value: 'quantitative' },
  { label: 'Nominal', value: 'nominal' },
]

const AGG_FUNCS = [
  { label: 'None', value: '' },
  { label: 'sum', value: 'sum' },
  { label: 'mean', value: 'mean' },
  { label: 'median', value: 'median' },
  { label: 'min', value: 'min' },
  { label: 'max', value: 'max' },
  { label: 'count', value: 'count' },
]

// Define configuration requirements for each chart type
const CHART_CONFIGS = {
  bar: {
    fields: ['x', 'y', 'color'],
    defaultTypes: { x: 'ordinal', y: 'quantitative', color: 'nominal' },
    defaultFields: { x: 'x', y: 'y', color: '' },
    showAggregate: false,
    showSize: false,
    description: 'Bar charts are used to compare values across different categories'
  },
  
  line: {
    fields: ['x', 'y', 'color'],
    defaultTypes: { x: 'ordinal', y: 'quantitative', color: 'nominal' },
    defaultFields: { x: 'x', y: 'y', color: '' },
    showAggregate: false,
    showSize: false,
    description: 'Line charts are used to display data trends over time or ordered categories'
  },
  
  scatter: {
    fields: ['x', 'y', 'color'],
    defaultTypes: { x: 'quantitative', y: 'quantitative', color: 'nominal' },
    defaultFields: { x: 'x', y: 'y', color: '' },
    showAggregate: false,
    showSize: false,
    description: 'Scatter plots are used to display correlations between two continuous variables'
  },
  
  bubble: {
    fields: ['x', 'y', 'color', 'size'],
    defaultTypes: { x: 'quantitative', y: 'quantitative', color: 'nominal', size: 'quantitative' },
    defaultFields: { x: 'x', y: 'y', color: '', size: 'size' },
    showAggregate: false,
    showSize: true,
    description: 'Bubble charts display third-dimensional data through bubble size'
  },
  
  pie: {
    fields: ['category', 'value'],
    defaultTypes: { category: 'nominal', value: 'quantitative' },
    defaultFields: { category: 'category', value: 'value' },
    showAggregate: false,
    showSize: false,
    description: 'Pie charts are used to display the proportional relationship of parts to the whole'
  },
  
  heatmap: {
    fields: ['x', 'y', 'value'],
    defaultTypes: { x: 'ordinal', y: 'ordinal', value: 'quantitative' },
    defaultFields: { x: 'x', y: 'y', value: 'value' },
    showAggregate: false,
    showSize: false,
    description: 'Heatmaps use color intensity to represent numerical values in a matrix'
  },
  
  treemap: {
    fields: ['category', 'size', 'color'],
    defaultTypes: { category: 'nominal', size: 'quantitative', color: 'nominal' },
    defaultFields: { category: 'category', size: 'size', color: 'category' },
    showAggregate: false,
    showSize: true,
    description: 'Treemaps use nested rectangles to represent hierarchical data'
  },
  
  // ECharts图表配置
  chord: {
    fields: ['source', 'target', 'value'],
    defaultTypes: { source: 'nominal', target: 'nominal', value: 'quantitative' },
    defaultFields: { source: 'source', target: 'target', value: 'value' },
    showAggregate: false,
    showSize: false,
    description: 'Chord charts are used to display connection relationships and strength between nodes'
  },
  
  funnel: {
    fields: ['stage', 'value', 'rate'],
    defaultTypes: { stage: 'ordinal', value: 'quantitative', rate: 'quantitative' },
    defaultFields: { stage: 'stage', value: 'value', rate: 'rate' },
    showAggregate: false,
    showSize: false,
    description: 'Funnel charts are used to display conversion rates at each stage of a process'
  },
  
  node_link: {
    fields: ['node', 'position_x', 'position_y', 'group', 'size', 'source', 'target', 'value'],
    defaultTypes: { node: 'nominal', position_x: 'quantitative', position_y: 'quantitative', group: 'nominal', size: 'quantitative', source: 'nominal', target: 'nominal', value: 'quantitative' },
    defaultFields: { node: 'node', position_x: 'x', position_y: 'y', group: 'group', size: 'size', source: 'source', target: 'target', value: 'value' },
    showAggregate: false,
    showSize: true,
    description: 'Node-link charts are used to display node positions and relationships in a network'
  },
  

  

}

function ChartConfig({ chartType, form, onFieldChange }) {
  const config = CHART_CONFIGS[chartType] || CHART_CONFIGS.bar
  
  // 获取字段标签
  const getFieldLabel = (field) => {
    const labels = {
      x: 'X Axis Field',
      y: 'Y Axis Field', 
      color: 'Color Field',
      size: 'Size Field',
      category: 'Category Field',
      value: 'Value Field',
      group: 'Group Field',
      dimension: 'Dimension Field',
      parent: 'Parent Field',
      source: 'Source Field',
      target: 'Target Field',
      node: 'Node Field',
      position_x: 'X Position Field',
      position_y: 'Y Position Field'
    }
    return labels[field] || field
  }
  
  // 获取字段占位符
  const getFieldPlaceholder = (field) => {
    const placeholders = {
      x: 'e.g.: category',
      y: 'e.g.: value', 
      color: 'e.g.: type',
      size: 'e.g.: size',
      category: 'e.g.: category',
      value: 'e.g.: value',
      group: 'e.g.: group',
      dimension: 'e.g.: dimension',
      parent: 'e.g.: parent',
      source: 'e.g.: source',
      target: 'e.g.: target',
      node: 'e.g.: node',
      position_x: 'e.g.: x',
      position_y: 'e.g.: y'
    }
    return placeholders[field] || `e.g.: ${field}`
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
        Field Configuration
      </div>
      {/* Dynamic field configuration */}
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
              label="Type" 
              name={`${field}Type`}
              style={{ minWidth: 140, marginBottom: 0 }}
            >
              <Select 
                id={`${field}Type`}
                options={field === 'color' && chartType === 'heatmap' ? COLOR_TYPES : FIELD_TYPES}
                placeholder="Select Type"
              />
            </Form.Item>
          </div>
        ))}
        </Space>
      </div>

      {/* Aggregation function */}
      {config.showAggregate && (
        <>
          <Divider style={{ margin: '16px 0 12px 0' }} />
          <Form.Item label="Aggregation Function" name="aggregate" style={{ marginBottom: 0 }}>
            <Select 
              id="aggregate"
              options={AGG_FUNCS} 
              style={{ width: 160 }} 
              placeholder="Select Aggregation Function"
            />
          </Form.Item>
        </>
      )}
    </div>
  )
}

export default ChartConfig