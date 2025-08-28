import { useEffect, useMemo, useState, useRef } from 'react'
import { Form, Input, Typography, theme, Button, Space, Select, Divider, InputNumber, message, ColorPicker } from 'antd'
import ChartConfig from './ChartConfig'
import StyleConfig from './StyleConfig'
import ChartFactory from './charts/ChartFactory'

const { Title } = Typography

function safeParseJSON(text) {
  try {
    if (!text || !text.trim()) return null
    return JSON.parse(text)
  } catch (e) {
    return null
  }
}

const CHART_TYPES = [
  { label: '柱状图 bar', value: 'bar' },
  { label: '箱线图 box', value: 'box' },
  { label: '气泡图 bubble', value: 'bubble' },
  { label: '填充气泡图 fill_bubble', value: 'fill_bubble' },
  { label: '和弦图 chord', value: 'chord' },
  { label: '漏斗图 funnel', value: 'funnel' },
  { label: '热力图 heatmap', value: 'heatmap' },
  { label: '折线图 line', value: 'line' },
  { label: '节点链接图 node_link', value: 'node_link' },
  { label: '平行坐标 parallel', value: 'parallel' },
  { label: '饼图 pie', value: 'pie' },
  { label: '散点图 scatter', value: 'scatter' },
  { label: '点图 point', value: 'point' },
  { label: '堆叠柱状图 stacked_bar', value: 'stacked_bar' },
  { label: '堆叠面积图 stacked_area', value: 'stacked_area' },
  { label: '流图 stream', value: 'stream' },
  { label: '脊线图 ridgeline', value: 'ridgeline' },
  { label: '小提琴图 violin', value: 'violin' },
  { label: '雷达图 radar', value: 'radar' },
  { label: '树状图 treemap', value: 'treemap' },
  { label: '树状图D3 treemap_D3', value: 'treemap_D3' },
  { label: '旭日图 sunburst', value: 'sunburst' },
  { label: '桑基图 sankey', value: 'sankey' },
]

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

function mapChartTypeToVegaMark(chartType) {
  switch (chartType) {
    case 'bar':
      return 'bar'
    case 'line':
      return 'line'
    case 'point':
      return 'point'
    case 'bubble':
    case 'fill_bubble':
      return 'circle'
    case 'box':
      return 'boxplot'
    case 'heatmap':
      return 'rect'
    case 'pie':
      return 'arc'
    case 'scatter':
      return 'point'
    case 'stacked_bar':
      return 'bar'
    case 'stacked_area':
      return 'area'
    case 'stream':
      return 'area'
    case 'ridgeline':
      return 'area'
    case 'violin':
      return 'area'
    case 'radar':
      return 'line'
    case 'treemap':
    case 'treemap_D3':
      return 'rect'
    case 'sunburst':
      return 'arc'
    case 'sankey':
      return 'rect'
    // Unsupported types fallback to bar so that preview still works
    case 'chord':
    case 'funnel':
    case 'node_link':
    case 'parallel':
    default:
      return 'bar'
  }
}

function mapVegaMarkToChartType(mark, encoding) {
  // 反向映射：从Vega-Lite mark类型映射回我们的图表类型
  const markType = typeof mark === 'string' ? mark : mark?.type || 'bar'
  
  switch (markType) {
    case 'bar':
      // 检查是否是堆叠柱状图
      if (encoding?.color) return 'stacked_bar'
      return 'bar'
    case 'line':
      // 检查是否是雷达图 (需要更复杂的判断逻辑)
      return 'line'
    case 'point':
      // 检查是否有size字段来区分point和scatter
      if (encoding?.size) return 'scatter'
      return 'point'
    case 'circle':
      // 气泡图
      return 'bubble'
    case 'boxplot':
      return 'box'
    case 'rect':
      // 检查是否是热力图 (有x, y, color编码)
      if (encoding?.x && encoding?.y && encoding?.color) return 'heatmap'
      return 'treemap'
    case 'arc':
      // 检查是否是旭日图还是饼图
      if (encoding?.theta) return 'pie'
      return 'sunburst'
    case 'area':
      // 根据编码判断具体的面积图类型
      if (encoding?.color) return 'stacked_area'
      return 'ridgeline'
    default:
      return 'bar'
  }
}

function pickFormFromSpec(spec) {
  if (!spec) return null
  try {
    const chartType = mapVegaMarkToChartType(spec.mark, spec.encoding)
    const encoding = spec.encoding || {}
    const mark = spec.mark || {}
    
    // 基础信息
    const result = {
      chartType,
      title: spec.title || '',
      description: spec.description || '',
      width: spec.width || undefined,
      height: spec.height || undefined,
      dataText: JSON.stringify(spec.data?.values ?? [], null, 2),
    }
    
    // 提取样式配置
    if (mark.color) result.markColor = mark.color
    if (mark.fill) result.fillColor = mark.fill
    if (mark.opacity !== undefined) result.opacity = mark.opacity
    if (mark.stroke) result.strokeColor = mark.stroke
    if (mark.strokeWidth !== undefined) result.strokeWidth = mark.strokeWidth
    if (mark.cornerRadius !== undefined) result.cornerRadius = mark.cornerRadius
    if (mark.size !== undefined) result.pointSize = mark.size
    if (mark.strokeDash) result.strokeDash = mark.strokeDash
    if (mark.innerRadius !== undefined) result.innerRadius = mark.innerRadius
    
    // 提取配置信息
    const config = spec.config || {}
    if (config.axis) {
      if (config.axis.x && config.axis.x.orient) result.xAxisPosition = config.axis.x.orient
      if (config.axis.y && config.axis.y.orient) result.yAxisPosition = config.axis.y.orient
      if (config.axis.grid === false) result.showGrid = false
    }
    if (config.legend) {
      if (config.legend.disable) result.showLegend = false
      if (config.legend.orient) result.legendPosition = config.legend.orient
      if (config.legend.direction) result.legendOrientation = config.legend.direction
    }
    
    // 提取字体配置
    if (config.title) {
      if (config.title.font) result.fontFamily = config.title.font
      if (config.title.fontSize) result.fontSize = config.title.fontSize
      if (config.title.color) result.fontColor = config.title.color
    }
    if (config.axis) {
      if (config.axis.labelFont) result.fontFamily = config.axis.labelFont
      if (config.axis.labelFontSize) result.fontSize = config.axis.labelFontSize
      if (config.axis.labelColor) result.fontColor = config.axis.labelColor
    }
    if (config.legend) {
      if (config.legend.labelFont) result.fontFamily = config.legend.labelFont
      if (config.legend.labelFontSize) result.fontSize = config.legend.labelFontSize
      if (config.legend.labelColor) result.fontColor = config.legend.labelColor
    }
    if (config.tooltip && config.tooltip.disable) result.enableTooltip = false
    if (spec.selection) {
      if (spec.selection.zoom) result.enableZoom = true
      if (spec.selection.pan) result.enablePan = true
      if (spec.selection.select) result.enableSelection = true
    }
    
    // 根据编码提取字段信息
    Object.entries(encoding).forEach(([key, value]) => {
      if (value && value.field) {
        // 将vega编码映射到我们的字段名
        let fieldName = key
        if (key === 'theta') fieldName = 'value' // 饼图的theta映射为value
        
        result[`${fieldName}Field`] = value.field
        result[`${fieldName}Type`] = value.type
        if (value.aggregate) result.aggregate = value.aggregate
        
        // 提取颜色配置
        if (key === 'color' && value.scale) {
          if (value.scale.scheme) {
            result.colorScheme = value.scale.scheme
          } else if (value.scale.range && value.scale.range.length === 1) {
            result.markColor = value.scale.range[0]
          }
        }
      }
    })
    
    return result
  } catch {
    return null
  }
}

function getDefaultData(chartType) {
  switch (chartType) {
    case 'line':
    case 'radar':
      return [
        { x: 'A', y: 28 }, { x: 'B', y: 55 }, { x: 'C', y: 43 }, { x: 'D', y: 91 }
      ]
    case 'point':
    case 'scatter':
    case 'bubble':
    case 'fill_bubble':
      return [
        { x: 5, y: 3, size: 10 }, { x: 10, y: 17, size: 30 }, { x: 15, y: 4, size: 15 }, { x: 20, y: 20, size: 45 }
      ]
    case 'heatmap':
      return [
        { x: 'A', y: 'K', value: 10 }, { x: 'A', y: 'L', value: 20 }, { x: 'B', y: 'K', value: 5 }, { x: 'B', y: 'L', value: 15 }
      ]
    case 'pie':
    case 'sunburst':
      return [
        { category: 'A', value: 28 }, { category: 'B', value: 55 }, { category: 'C', value: 43 }, { category: 'D', value: 91 }
      ]
    case 'stacked_bar':
      return [
        { x: 'A', y: 28, category: 'Type1' }, { x: 'A', y: 25, category: 'Type2' },
        { x: 'B', y: 55, category: 'Type1' }, { x: 'B', y: 35, category: 'Type2' },
        { x: 'C', y: 43, category: 'Type1' }, { x: 'C', y: 30, category: 'Type2' }
      ]
    case 'stacked_area':
    case 'stream':
      return [
        { x: 1, y: 28, category: 'Type1' }, { x: 1, y: 25, category: 'Type2' },
        { x: 2, y: 55, category: 'Type1' }, { x: 2, y: 35, category: 'Type2' },
        { x: 3, y: 43, category: 'Type1' }, { x: 3, y: 30, category: 'Type2' },
        { x: 4, y: 61, category: 'Type1' }, { x: 4, y: 40, category: 'Type2' }
      ]
    case 'ridgeline':
    case 'violin':
      return [
        { group: 'A', value: 10 }, { group: 'A', value: 15 }, { group: 'A', value: 20 },
        { group: 'B', value: 25 }, { group: 'B', value: 30 }, { group: 'B', value: 35 },
        { group: 'C', value: 40 }, { group: 'C', value: 45 }, { group: 'C', value: 50 }
      ]
    case 'treemap':
    case 'treemap_D3':
      return [
        { category: 'A', size: 100 }, { category: 'B', size: 200 }, 
        { category: 'C', size: 150 }, { category: 'D', size: 80 }
      ]
    case 'sankey':
      return [
        { source: 'A', target: 'X', value: 10 },
        { source: 'A', target: 'Y', value: 15 },
        { source: 'B', target: 'X', value: 20 },
        { source: 'B', target: 'Z', value: 25 }
      ]
    case 'box':
      return [
        { group: 'A', value: 10 }, { group: 'A', value: 15 }, { group: 'A', value: 20 }, { group: 'A', value: 25 },
        { group: 'B', value: 30 }, { group: 'B', value: 35 }, { group: 'B', value: 40 }, { group: 'B', value: 45 }
      ]
    case 'bar':
    case 'chord':
    case 'funnel':
    case 'node_link':
    case 'parallel':
    default:
      return [
        { x: 'A', y: 28 }, { x: 'B', y: 55 }, { x: 'C', y: 43 }, { x: 'D', y: 91 }, { x: 'E', y: 81 }
      ]
  }
}

function ChartEditor({ specText, onChange, onSave }) {
  const { token } = theme.useToken()
  const [form] = Form.useForm()

  // 简化的状态管理 - 初始状态为空
  const [chartType, setChartType] = useState('')
  const [formValues, setFormValues] = useState({})
  const [dataText, setDataText] = useState('[]')
  const [isInitialized, setIsInitialized] = useState(false)

  // 保存 Vega view 与容器引用以便截图
  const viewRef = useRef(null)
  const embedContainerRef = useRef(null)

  // 防止循环更新的标志
  const isUpdatingFromExternal = useRef(false)
  const isInternalUpdate = useRef(false)
  
  // 只有外部传入有效的specText时才处理（从历史记录选择时）
  useEffect(() => {
    // 如果是内部更新导致的变化，忽略
    if (isUpdatingFromExternal.current || isInternalUpdate.current) {
      return
    }
    
    // 只有当外部传入了非空的specText时才处理
    if (specText && specText.trim() && specText !== '{}') {
      const spec = safeParseJSON(specText)
      const mapped = pickFormFromSpec(spec)
      if (mapped && mapped.chartType) {
        setChartType(mapped.chartType)
        setFormValues(mapped)
        setDataText(mapped.dataText || JSON.stringify(getDefaultData(mapped.chartType), null, 2))
        setIsInitialized(true)
        form.setFieldsValue(mapped)
      }
    }
  }, [specText, form])

  // 基于表单字段构建规范
  const dataValues = useMemo(() => {
    const parsed = safeParseJSON(dataText)
    return Array.isArray(parsed) ? parsed : []
  }, [dataText])

  // 同步到外部 specText - 现在由各个图表组件处理
  useEffect(() => {
    // 只有在用户已经选择了图表类型后才同步
    if (chartType && !isUpdatingFromExternal.current) {
      isUpdatingFromExternal.current = true
      // 这里可以添加同步逻辑，如果需要的话
      setTimeout(() => {
        isUpdatingFromExternal.current = false
      }, 100)
    }
  }, [chartType])

  // 获取默认配置的辅助函数
  const getDefaultConfig = (chartType) => {
    const CHART_CONFIGS = {
      pie: { categoryField: 'category', valueField: 'value' },
      sunburst: { categoryField: 'category', valueField: 'value' },
      heatmap: { xField: 'x', yField: 'y', valueField: 'value' },
      box: { groupField: 'group', valueField: 'value' },
      violin: { groupField: 'group', valueField: 'value' },
      ridgeline: { groupField: 'group', valueField: 'value' },
      treemap: { categoryField: 'category', sizeField: 'size' },
      treemap_D3: { categoryField: 'category', sizeField: 'size' },
      sankey: { sourceField: 'source', targetField: 'target', valueField: 'value' },
      point: { xField: 'x', yField: 'y', sizeField: 'size' },
      scatter: { xField: 'x', yField: 'y', sizeField: 'size' },
      bubble: { xField: 'x', yField: 'y', sizeField: 'size' },
      fill_bubble: { xField: 'x', yField: 'y', sizeField: 'size' },
    }
    return CHART_CONFIGS[chartType] || { xField: 'x', yField: 'y' }
  }

  const handleSave = async () => {
    // 这里需要从图表组件获取当前的spec
    try {
      let dataUrl = ''
      const view = viewRef.current
      if (view && typeof view.toCanvas === 'function') {
        try {
          const canvas = await view.toCanvas()
          dataUrl = canvas.toDataURL('image/png')
        } catch {}
      }
      if (!dataUrl) {
        const container = embedContainerRef.current
        if (container) {
          const canvas = container.querySelector('canvas')
          if (canvas && typeof canvas.toDataURL === 'function') {
            dataUrl = canvas.toDataURL('image/png')
          } else {
            const svg = container.querySelector('svg')
            if (svg) {
              const svgData = new XMLSerializer().serializeToString(svg)
              const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
              const url = URL.createObjectURL(svgBlob)
              const image = new Image()
              dataUrl = await new Promise((resolve) => {
                image.onload = () => {
                  const c = document.createElement('canvas')
                  c.width = svg.clientWidth || 300
                  c.height = svg.clientHeight || 200
                  const ctx = c.getContext('2d')
                  ctx.drawImage(image, 0, 0)
                  URL.revokeObjectURL(url)
                  resolve(c.toDataURL('image/png'))
                }
                image.onerror = () => resolve('')
                image.src = url
              })
            }
          }
        }
      }
      // 暂时使用空字符串，后续可以从图表组件获取
      onSave?.({ specText: '', thumbDataUrl: dataUrl })
    } catch (e) {
      onSave?.({ specText: '', thumbDataUrl: '' })
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', width: '100%', minWidth: 0, gap: 12 }}>
      <Space align="center" style={{ justifyContent: 'space-between' }}>
        <Title level={5} style={{ marginTop: 0, marginBottom: 0 }}>Vega-Lite 图表编辑器</Title>
        <Button type="primary" size="small" onClick={handleSave}>保存到历史</Button>
      </Space>

      <Form
        form={form}
        layout="vertical"
        initialValues={{
          chartType: '',
          dataText: '[]',
          opacity: 1.0,
          strokeWidth: 0,
          cornerRadius: 0,
          showLegend: true,
          enableTooltip: true,
          showGrid: true
        }}
        onValuesChange={(changed, all) => {
          // 设置内部更新标志
          isInternalUpdate.current = true
          
          // 处理图表类型变化
          if ('chartType' in changed && changed.chartType) {
            const next = changed.chartType
            setChartType(next)
            setDataText(JSON.stringify(getDefaultData(next), null, 2))
            setIsInitialized(true)
            
            // 根据图表类型设置默认字段配置
            const defaultConfig = getDefaultConfig(next)
            const updatedValues = { 
              ...all, 
              ...defaultConfig,
              dataText: JSON.stringify(getDefaultData(next), null, 2)
            }
            
            // 设置表单值和状态
            setTimeout(() => {
              form.setFieldsValue(updatedValues)
              setFormValues(updatedValues)
              isInternalUpdate.current = false
            }, 0)
          } else {
            // 其他字段变化
            setFormValues(all)
            
            // 处理数据文本变化
            if ('dataText' in changed) {
              setDataText(all.dataText)
            }
            
            setTimeout(() => {
              isInternalUpdate.current = false
            }, 0)
          }
        }}
      >
        {/* 基础配置 */}
        <Space size={12} wrap>
          <Form.Item label="图表类型" name="chartType" style={{ minWidth: 160 }}>
            <Select 
              id="chartType"
              options={CHART_TYPES} 
              placeholder="请选择图表类型"
              allowClear
            />
          </Form.Item>
          
          {chartType && (
            <>
              <Form.Item label="标题" name="title" style={{ minWidth: 240 }}>
                <Input id="title" placeholder="可选" />
              </Form.Item>
              <Form.Item label="描述" name="description" style={{ minWidth: 300 }}>
                <Input id="description" placeholder="可选" />
              </Form.Item>
              <Form.Item label="宽度" name="width">
                <InputNumber id="width" min={0} style={{ width: 120 }} placeholder="auto" />
              </Form.Item>
              <Form.Item label="高度" name="height">
                <InputNumber id="height" min={0} style={{ width: 120 }} placeholder="auto" />
              </Form.Item>
            </>
          )}
        </Space>

        {/* 只有选择了图表类型才显示动态配置 */}
        {chartType && (
          <>
            <ChartConfig 
              chartType={chartType} 
              form={form}
              onFieldChange={(field, value) => {
                setFormValues(prev => ({ ...prev, [field]: value }))
              }}
            />

            {/* 样式配置 */}
            <StyleConfig chartType={chartType} form={form} />

            <Form.Item label="数据（JSON 数组）" name="dataText">
              <Input.TextArea 
                id="dataText"
                autoSize={{ minRows: 6, maxRows: 12 }} 
                placeholder='例如:[{"x":"A","y":10}]' 
              />
            </Form.Item>
          </>
        )}
      </Form>

      <div ref={embedContainerRef} style={{ flex: 1, minHeight: 200, border: `1px dashed ${token.colorBorder}`, borderRadius: 8, display: 'flex', alignItems: 'stretch', justifyContent: 'stretch', padding: 8, overflow: 'hidden' }}>
        {chartType ? (
          <ChartFactory
            chartType={chartType}
            title={formValues.title}
            description={formValues.description}
            width={formValues.width}
            height={formValues.height}
            formValues={formValues}
            dataValues={dataValues}
            onEmbed={(result) => { viewRef.current = result.view }}
          />
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: token.colorTextSecondary }}>
            请选择图表类型以开始配置
          </div>
        )}
      </div>
    </div>
  )
}

export default ChartEditor       