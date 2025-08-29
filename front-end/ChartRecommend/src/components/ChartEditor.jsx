import { useEffect, useMemo, useState, useRef } from 'react'
import { Form, Input, Typography, theme, Button, Space, Select, Divider, InputNumber, message, ColorPicker, Table } from 'antd'
import ChartConfig from './ChartConfig'
import StyleConfig from './StyleConfig'
import DataTableEditor from './DataTableEditor'
import ChartFactory from './charts/ChartFactory'
import { buildBarChartSpec } from './charts/BarChart'
import { buildLineChartSpec } from './charts/LineChart'
import { buildPieChartSpec } from './charts/PieChart'
import { buildScatterChartSpec } from './charts/ScatterChart'
import { buildHeatmapChartSpec } from './charts/HeatmapChart'
import { buildAreaChartSpec } from './charts/AreaChart'
import { buildBoxChartSpec } from './charts/BoxChart'
import { buildGenericChartSpec } from './charts/GenericChart'

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
      // 柱状图：检查是否有stack属性来判断是否为堆叠柱状图
      if (encoding?.y?.stack) return 'stacked_bar'
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
    if (mark.opacity !== undefined) result.opacity = mark.opacity
    if (mark.strokeWidth !== undefined) result.strokeWidth = mark.strokeWidth
    if (mark.cornerRadius !== undefined) result.cornerRadius = mark.cornerRadius
    if (mark.size !== undefined) result.pointSize = mark.size
    if (mark.strokeDash) result.strokeDash = mark.strokeDash
    if (mark.innerRadius !== undefined) result.innerRadius = mark.innerRadius
    
    // 提取配置信息
    const config = spec.config || {}
    if (config.axis) {
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
    }
    if (config.axis) {
      if (config.axis.labelFont) result.fontFamily = config.axis.labelFont
      if (config.axis.labelFontSize) result.fontSize = config.axis.labelFontSize
    }
    if (config.legend) {
      if (config.legend.labelFont) result.fontFamily = config.legend.labelFont
      if (config.legend.labelFontSize) result.fontSize = config.legend.labelFontSize
    }

    
    // 根据编码提取字段信息
    Object.entries(encoding).forEach(([key, value]) => {
      if (value && value.field) {
        // 将vega编码映射到我们的字段名
        let fieldName = key
        if (key === 'theta') fieldName = 'value' // 饼图的theta映射为value
        
        result[`${fieldName}Field`] = value.field
        result[`${fieldName}Type`] = value.type
        

      }
    })
    
    return result
  } catch {
    return null
  }
}

function getDefaultData(chartType) {
  switch (chartType) {
    case 'bar':
    case 'line':
    case 'stacked_bar':
      return [
        { category: '类别A', value: 10 },
        { category: '类别B', value: 20 },
        { category: '类别C', value: 15 },
        { category: '类别D', value: 25 }
      ]
    case 'scatter':
    case 'bubble':
    case 'point':
      return [
        { x: 10, y: 15, size: 20, category: 'A类' },
        { x: 20, y: 25, size: 35, category: 'A类' },
        { x: 30, y: 35, size: 50, category: 'B类' },
        { x: 40, y: 45, size: 65, category: 'B类' }
      ]
    case 'pie':
    case 'sunburst':
      return [
        { category: '分类A', value: 30 },
        { category: '分类B', value: 25 },
        { category: '分类C', value: 20 },
        { category: '分类D', value: 15 },
        { category: '分类E', value: 10 }
      ]
    case 'heatmap':
      return [
        { x: 'A', y: 'X', value: 10 },
        { x: 'A', y: 'Y', value: 20 },
        { x: 'B', y: 'X', value: 15 },
        { x: 'B', y: 'Y', value: 25 },
        { x: 'C', y: 'X', value: 30 },
        { x: 'C', y: 'Y', value: 35 }
      ]
    case 'area':
    case 'stacked_area':
    case 'stream':
      return [
        { time: '2023-01', value: 10, series: '系列A' },
        { time: '2023-02', value: 20, series: '系列A' },
        { time: '2023-03', value: 15, series: '系列A' },
        { time: '2023-01', value: 5, series: '系列B' },
        { time: '2023-02', value: 15, series: '系列B' },
        { time: '2023-03', value: 25, series: '系列B' }
      ]
    case 'radar':
      return [
        { x: 'A', y: 28 }, { x: 'B', y: 55 }, { x: 'C', y: 43 }, { x: 'D', y: 91 }
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
    case 'chord':
    case 'funnel':
    case 'node_link':
    case 'parallel':
    default:
      return [
        { x: 1, y: 10 },
        { x: 2, y: 20 },
        { x: 3, y: 15 },
        { x: 4, y: 25 }
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
  const [tableData, setTableData] = useState([])
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
        
        // 解析数据并设置到表格
        try {
          const parsedData = JSON.parse(mapped.dataText || '[]')
          setTableData(Array.isArray(parsedData) ? parsedData : [])
        } catch {
          setTableData([])
        }
        
        setIsInitialized(true)
        form.setFieldsValue(mapped)
      }
    }
  }, [specText, form])

  // 基于表单字段构建规范
  const dataValues = useMemo(() => {
    // 优先使用表格数据，如果没有则使用JSON数据
    if (tableData && tableData.length > 0) {
      return tableData
    }
    const parsed = safeParseJSON(dataText)
    return Array.isArray(parsed) ? parsed : []
  }, [tableData, dataText])

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

  // 根据表单值生成Vega-Lite规范的函数
  const buildSpecFromForm = () => {
    if (!chartType || !formValues) return null
    
    // 获取当前表单值
    const currentFormValues = form.getFieldsValue()
    // 优先使用表格数据
    const currentDataValues = tableData && tableData.length > 0 ? tableData : (safeParseJSON(dataText) || [])
    
    // 构建spec参数
    const specParams = {
      title: currentFormValues.title,
      description: currentFormValues.description,
      width: currentFormValues.width,
      height: currentFormValues.height,
      formValues: { ...currentFormValues, dataText },
      dataValues: currentDataValues
    }
    
    // 根据图表类型调用对应的构建函数
    switch (chartType) {
      case 'bar':
        return buildBarChartSpec(specParams)
      case 'stacked_bar':
        // 堆叠柱状图需要特殊的处理
        const stackedParams = {
          ...specParams,
          formValues: {
            ...specParams.formValues,
            isStacked: true
          }
        }
        return buildBarChartSpec(stackedParams)
      case 'line':
      case 'radar':
        return buildLineChartSpec(specParams)
      case 'pie':
      case 'sunburst':
        return buildPieChartSpec(specParams)
      case 'point':
      case 'scatter':
      case 'bubble':
      case 'fill_bubble':
        return buildScatterChartSpec(specParams)
      case 'heatmap':
        return buildHeatmapChartSpec(specParams)
      case 'stacked_area':
      case 'stream':
      case 'ridgeline':
      case 'violin':
        return buildAreaChartSpec(specParams)
      case 'box':
        return buildBoxChartSpec(specParams)
      default:
        return buildGenericChartSpec({ ...specParams, chartType })
    }
  }

  const handleSave = async () => {
    try {
      // 生成当前的Vega-Lite规范
      const spec = buildSpecFromForm()
      const specText = spec ? JSON.stringify(spec, null, 2) : ''
      
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
      
      // 保存包含完整规范的图表
      onSave?.({ specText, thumbDataUrl: dataUrl })
    } catch (e) {
      console.error('保存图表时出错:', e)
      onSave?.({ specText: '', thumbDataUrl: '' })
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', width: '100%', minWidth: 0, gap: 16 }}>
      <Space align="center" style={{ justifyContent: 'space-between', marginBottom: 8 }}>
        <Title level={5} style={{ marginTop: 0, marginBottom: 0 }}>Vega-Lite 图表编辑器</Title>
        <Button type="primary" size="small" onClick={handleSave}>保存到历史</Button>
      </Space>

      <Form
        form={form}
        // layout="vertical"
        layout="horizontal"
        initialValues={{
          chartType: '',
          dataText: '[]',
          opacity: 1.0,
          strokeWidth: 0,
          cornerRadius: 0,
          showLegend: true,
          showGrid: true
        }}
        onValuesChange={(changed, all) => {
          // 设置内部更新标志
          isInternalUpdate.current = true
          
          // 处理图表类型变化
          if ('chartType' in changed && changed.chartType) {
            const next = changed.chartType
            setChartType(next)
            const defaultData = getDefaultData(next)
            setDataText(JSON.stringify(defaultData, null, 2))
            setTableData(defaultData) // 同时设置表格数据
            setIsInitialized(true)
            
            // 根据图表类型设置默认字段配置
            const defaultConfig = getDefaultConfig(next)
            const updatedValues = { 
              ...all, 
              ...defaultConfig,
              dataText: JSON.stringify(defaultData, null, 2)
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
        <Space size={12} wrap style={{ marginBottom: 16 }}>
          <Form.Item label="图表类型" name="chartType" style={{ minWidth: 160, marginBottom: 12 }}>
            <Select 
              id="chartType"
              options={CHART_TYPES} 
              placeholder="请选择图表类型"
              allowClear
            />
          </Form.Item>
          
          {chartType && (
            <>
              <Form.Item label="标题" name="title" style={{ minWidth: 200, marginBottom: 12 }}>
                <Input id="title" placeholder="可选" />
              </Form.Item>
              <Form.Item label="描述" name="description" style={{ minWidth: 250, marginBottom: 12 }}>
                <Input id="description" placeholder="可选" />
              </Form.Item>
              <Form.Item label="宽度" name="width" style={{ marginBottom: 12 }}>
                <InputNumber id="width" min={0} style={{ width: 100 }} placeholder="auto" />
              </Form.Item>
              <Form.Item label="高度" name="height" style={{ marginBottom: 12 }}>
                <InputNumber id="height" min={0} style={{ width: 100 }} placeholder="auto" />
              </Form.Item>
            </>
          )}
        </Space>

        {/* 只有选择了图表类型才显示动态配置 */}
        {chartType && (
          <div style={{ display: 'flex', gap: '16px', marginTop: '16px' }}>
            {/* 左侧：字段配置和样式配置 */}
            <div style={{ flex: 1 }}>
              <ChartConfig 
                chartType={chartType} 
                form={form}
                onFieldChange={(field, value) => {
                  setFormValues(prev => ({ ...prev, [field]: value }))
                }}
              />
              
              <StyleConfig chartType={chartType} form={form} />
            </div>

            {/* 中间分割线 */}
            <Divider type="vertical" style={{ height: 'auto', margin: '0 4px' }} />

            {/* 右侧：数据输入 */}
            <div style={{ flex: 1 }}>
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: '14px', fontWeight: 500, marginBottom: 12, color: '#262626' }}>
                  JSON数据编辑器
                </div>
                <DataTableEditor
                  value={tableData}
                  onChange={setTableData}
                  chartType={chartType}
                />
              </div>
            </div>
          </div>
        )}
      </Form>

      <div ref={embedContainerRef} style={{ flex: 1, minHeight: 180, border: `1px dashed ${token.colorBorder}`, borderRadius: 8, display: 'flex', alignItems: 'stretch', justifyContent: 'stretch', padding: 12, overflow: 'hidden' }}>
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