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
    showAggregate: true,
    showSize: false,
    description: '柱状图用于比较不同类别的数值'
  },
  
  line: {
    fields: ['x', 'y', 'color'],
    defaultTypes: { x: 'ordinal', y: 'quantitative', color: 'nominal' },
    defaultFields: { x: 'x', y: 'y', color: '' },
    showAggregate: true,
    showSize: false,
    description: '折线图用于显示数据随时间或有序类别的变化趋势'
  },
  
  point: {
    fields: ['x', 'y', 'color', 'size'],
    defaultTypes: { x: 'quantitative', y: 'quantitative', color: 'nominal', size: 'quantitative' },
    defaultFields: { x: 'x', y: 'y', color: '', size: 'size' },
    showAggregate: false,
    showSize: true,
    description: '点图用于显示两个数值变量之间的关系'
  },
  
  scatter: {
    fields: ['x', 'y', 'color', 'size'],
    defaultTypes: { x: 'quantitative', y: 'quantitative', color: 'nominal', size: 'quantitative' },
    defaultFields: { x: 'x', y: 'y', color: '', size: 'size' },
    showAggregate: false,
    showSize: true,
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
  
  fill_bubble: {
    fields: ['x', 'y', 'color', 'size'],
    defaultTypes: { x: 'quantitative', y: 'quantitative', color: 'nominal', size: 'quantitative' },
    defaultFields: { x: 'x', y: 'y', color: '', size: 'size' },
    showAggregate: false,
    showSize: true,
    description: '填充气泡图是带有填充颜色的气泡图'
  },
  
  pie: {
    fields: ['category', 'value'],
    defaultTypes: { category: 'nominal', value: 'quantitative' },
    defaultFields: { category: 'category', value: 'value' },
    showAggregate: true,
    showSize: false,
    description: '饼图用于显示各部分占整体的比例关系'
  },
  
  heatmap: {
    fields: ['x', 'y', 'value'],
    defaultTypes: { x: 'ordinal', y: 'ordinal', value: 'quantitative' },
    defaultFields: { x: 'x', y: 'y', value: 'value' },
    showAggregate: true,
    showSize: false,
    description: '热力图用颜色深浅表示数值大小的矩阵图'
  },
  
  box: {
    fields: ['group', 'value'],
    defaultTypes: { group: 'nominal', value: 'quantitative' },
    defaultFields: { group: 'group', value: 'value' },
    showAggregate: false,
    showSize: false,
    description: '箱线图显示数据的分布情况和异常值'
  },
  
  violin: {
    fields: ['group', 'value'],
    defaultTypes: { group: 'nominal', value: 'quantitative' },
    defaultFields: { group: 'group', value: 'value' },
    showAggregate: false,
    showSize: false,
    description: '小提琴图结合了箱线图和密度图的特点'
  },
  
  stacked_bar: {
    fields: ['x', 'y', 'color'],
    defaultTypes: { x: 'ordinal', y: 'quantitative', color: 'nominal' },
    defaultFields: { x: 'x', y: 'y', color: 'category' },
    showAggregate: true,
    showSize: false,
    description: '堆叠柱状图显示分类数据的组成结构'
  },
  
  stacked_area: {
    fields: ['x', 'y', 'color'],
    defaultTypes: { x: 'ordinal', y: 'quantitative', color: 'nominal' },
    defaultFields: { x: 'x', y: 'y', color: 'category' },
    showAggregate: true,
    showSize: false,
    description: '堆叠面积图展示数据随时间的变化和组成'
  },
  
  stream: {
    fields: ['x', 'y', 'color'],
    defaultTypes: { x: 'ordinal', y: 'quantitative', color: 'nominal' },
    defaultFields: { x: 'x', y: 'y', color: 'category' },
    showAggregate: true,
    showSize: false,
    description: '流图是围绕中轴线对称的堆叠面积图'
  },
  
  ridgeline: {
    fields: ['group', 'value'],
    defaultTypes: { group: 'nominal', value: 'quantitative' },
    defaultFields: { group: 'group', value: 'value' },
    showAggregate: false,
    showSize: false,
    description: '脊线图显示多个分组的密度分布'
  },
  
  radar: {
    fields: ['dimension', 'value', 'group'],
    defaultTypes: { dimension: 'nominal', value: 'quantitative', group: 'nominal' },
    defaultFields: { dimension: 'x', value: 'y', group: '' },
    showAggregate: false,
    showSize: false,
    description: '雷达图在极坐标系中显示多维数据'
  },
  
  treemap: {
    fields: ['category', 'size', 'color'],
    defaultTypes: { category: 'nominal', size: 'quantitative', color: 'nominal' },
    defaultFields: { category: 'category', size: 'size', color: 'category' },
    showAggregate: false,
    showSize: true,
    description: '树状图用嵌套矩形表示层次数据'
  },
  
  treemap_D3: {
    fields: ['category', 'size', 'color'],
    defaultTypes: { category: 'nominal', size: 'quantitative', color: 'nominal' },
    defaultFields: { category: 'category', size: 'size', color: 'category' },
    showAggregate: false,
    showSize: true,
    description: 'D3样式的树状图'
  },
  
  sunburst: {
    fields: ['category', 'value', 'parent'],
    defaultTypes: { category: 'nominal', value: 'quantitative', parent: 'nominal' },
    defaultFields: { category: 'category', value: 'value', parent: '' },
    showAggregate: false,
    showSize: false,
    description: '旭日图用同心圆环表示层次数据'
  },
  
  sankey: {
    fields: ['source', 'target', 'value'],
    defaultTypes: { source: 'nominal', target: 'nominal', value: 'quantitative' },
    defaultFields: { source: 'source', target: 'target', value: 'value' },
    showAggregate: false,
    showSize: false,
    description: '桑基图显示流量在不同节点间的分布'
  },
  
  // 暂不支持的复杂图表类型，使用默认配置
  chord: {
    fields: ['x', 'y'],
    defaultTypes: { x: 'ordinal', y: 'quantitative' },
    defaultFields: { x: 'x', y: 'y' },
    showAggregate: true,
    showSize: false,
    description: '和弦图（暂未完全支持，显示为柱状图）'
  },
  
  funnel: {
    fields: ['x', 'y'],
    defaultTypes: { x: 'ordinal', y: 'quantitative' },
    defaultFields: { x: 'x', y: 'y' },
    showAggregate: true,
    showSize: false,
    description: '漏斗图（暂未完全支持，显示为柱状图）'
  },
  
  node_link: {
    fields: ['x', 'y'],
    defaultTypes: { x: 'ordinal', y: 'quantitative' },
    defaultFields: { x: 'x', y: 'y' },
    showAggregate: true,
    showSize: false,
    description: '节点链接图（暂未完全支持，显示为柱状图）'
  },
  
  parallel: {
    fields: ['x', 'y'],
    defaultTypes: { x: 'ordinal', y: 'quantitative' },
    defaultFields: { x: 'x', y: 'y' },
    showAggregate: true,
    showSize: false,
    description: '平行坐标图（暂未完全支持，显示为柱状图）'
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
      {/* 图表描述 */}
      <div style={{ 
        padding: '8px 12px', 
        background: '#f0f9ff', 
        border: '1px solid #bae6fd', 
        borderRadius: '6px',
        marginBottom: '16px',
        fontSize: '14px',
        color: '#0369a1'
      }}>
        💡 {config.description}
      </div>

      <Divider style={{ margin: '12px 0' }} />

      {/* 动态字段配置 */}
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