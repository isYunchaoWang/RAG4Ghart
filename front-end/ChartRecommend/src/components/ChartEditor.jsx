import { useEffect, useMemo, useState, useRef } from 'react'
import { Form, Input, Typography, theme, Button, Space, Select, Divider, InputNumber, message, ColorPicker, Table } from 'antd'
import ChartConfig from './ChartConfig'
import StyleConfig from './StyleConfig'
import DataTableEditor from './DataTableEditor'
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
  { label: '气泡图 bubble', value: 'bubble' },
  { label: '环状关系图 chord', value: 'chord' },
  { label: '漏斗图 funnel', value: 'funnel' },
  { label: '折线图 line', value: 'line' },
  { label: '关系图 nodelink', value: 'nodelink' },
  { label: '饼图 pie', value: 'pie' },
  { label: '散点图 scatter', value: 'scatter' },
  { label: '矩形树图 treemap', value: 'treemap' },
]

// 获取图表类型的中文标签
const getChartTypeLabel = (chartType) => {
  const chartTypeObj = CHART_TYPES.find(item => item.value === chartType)
  return chartTypeObj ? chartTypeObj.label.split(' ')[0] : chartType
}

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
    case 'scatter':
      return 'point'
    case 'bubble':
      return 'circle'
    case 'heatmap':
      return 'rect'
    case 'pie':
      return 'arc'
    case 'treemap':
      return 'rect'
    case 'chord':
      return 'chord'
    case 'funnel':
      return 'funnel'
    case 'nodelink':
      return 'nodelink'
    default:
      return 'bar'
  }
}

function mapVegaMarkToChartType(mark, encoding) {
  // 反向映射：从Vega-Lite mark类型映射回我们的图表类型
  const markType = typeof mark === 'string' ? mark : mark?.type || 'bar'
  
  switch (markType) {
    case 'bar':
      return 'bar'
    case 'line':
      return 'line'
    case 'point':
      return 'scatter'
    case 'circle':
      return 'bubble'
    case 'rect':
      if (encoding?.x && encoding?.y && encoding?.color) return 'heatmap'
      return 'treemap'
    case 'arc':
      return 'pie'
    case 'chord':
      return 'chord'
    case 'funnel':
      return 'funnel'
    case 'nodelink':
      return 'nodelink'
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
      return [
        { x: 'A', y: 10 },
        { x: 'B', y: 20 },
        { x: 'C', y: 15 },
        { x: 'D', y: 25 }
      ]
    case 'line':
      return [
        { x: '2023-01', y: 10 },
        { x: '2023-02', y: 20 },
        { x: '2023-03', y: 15 },
        { x: '2023-04', y: 25 }
      ]
    case 'scatter':
      return [
        { x: 10, y: 15, category: 'A类' },
        { x: 20, y: 25, category: 'A类' },
        { x: 30, y: 35, category: 'B类' },
        { x: 40, y: 45, category: 'B类' }
      ]
    case 'bubble':
      return [
        { x: 10, y: 15, size: 20, category: 'A类' },
        { x: 20, y: 25, size: 35, category: 'A类' },
        { x: 30, y: 35, size: 50, category: 'B类' },
        { x: 40, y: 45, size: 65, category: 'B类' }
      ]
    case 'pie':
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
    case 'treemap':
      return [
        { category: '电子产品', size: 300, color: '科技' },
        { category: '服装', size: 250, color: '时尚' },
        { category: '食品', size: 200, color: '生活' },
        { category: '图书', size: 150, color: '教育' },
        { category: '家居', size: 180, color: '生活' },
        { category: '运动', size: 120, color: '健康' },
        { category: '美妆', size: 160, color: '时尚' },
        { category: '汽车', size: 220, color: '交通' },
        { category: '游戏', size: 140, color: '娱乐' },
        { category: '音乐', size: 90, color: '娱乐' }
      ]
    case 'chord':
      return [
        { source: '北京', target: '上海', value: 25 },
        { source: '北京', target: '广州', value: 18 },
        { source: '北京', target: '深圳', value: 15 },
        { source: '北京', target: '杭州', value: 12 },
        { source: '上海', target: '广州', value: 22 },
        { source: '上海', target: '深圳', value: 20 },
        { source: '上海', target: '杭州', value: 28 },
        { source: '上海', target: '南京', value: 16 },
        { source: '广州', target: '深圳', value: 30 },
        { source: '广州', target: '杭州', value: 14 },
        { source: '广州', target: '成都', value: 18 },
        { source: '深圳', target: '杭州', value: 10 },
        { source: '深圳', target: '成都', value: 12 },
        { source: '杭州', target: '南京', value: 22 },
        { source: '杭州', target: '成都', value: 16 },
        { source: '南京', target: '成都', value: 14 },
        { source: '南京', target: '武汉', value: 20 },
        { source: '成都', target: '武汉', value: 18 },
        { source: '武汉', target: '西安', value: 24 },
        { source: '成都', target: '西安', value: 16 },
        { source: '西安', target: '北京', value: 20 }
      ]
    case 'funnel':
      return [
        { stage: '访问', value: 1000, rate: 1.0 },
        { stage: '注册', value: 800, rate: 0.8 },
        { stage: '下载', value: 600, rate: 0.6 },
        { stage: '购买', value: 200, rate: 0.2 },
        { stage: '复购', value: 80, rate: 0.08 }
      ]
    case 'nodelink':
      return [
        { node: 'A', x: 10, y: 20, group: '组1', size: 30 },
        { node: 'B', x: 30, y: 40, group: '组1', size: 25 },
        { node: 'C', x: 50, y: 30, group: '组2', size: 35 },
        { node: 'D', x: 70, y: 60, group: '组2', size: 20 },
        { node: 'E', x: 90, y: 10, group: '组3', size: 40 },
        { source: 'A', target: 'B', value: 1 },
        { source: 'B', target: 'C', value: 1 },
        { source: 'C', target: 'D', value: 1 },
        { source: 'D', target: 'E', value: 1 },
        { source: 'A', target: 'E', value: 1 }
      ]
    default:
      return [
        { x: 1, y: 10 },
        { x: 2, y: 20 },
        { x: 3, y: 15 },
        { x: 4, y: 25 }
      ]
  }
}

function ChartEditor({ specText, onChange, onSave, selectedChartType }) {
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
  
  // 处理从检索结果选择的图表类型
  useEffect(() => {
    if (selectedChartType && selectedChartType !== chartType) {
      console.log('从检索结果选择图表类型:', selectedChartType)
      handleCreateNewChart(selectedChartType)
    }
  }, [selectedChartType])

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
        
        // 更新全局变量，用于检测重复选择
        window.lastSelectedChartType = mapped.chartType
        console.log('从历史记录加载，更新lastSelectedChartType:', mapped.chartType)
      }
    } else if (!specText || specText.trim() === '' || specText === '{}') {
      // 如果外部清空了specText，重置状态
      setChartType('')
      setFormValues({})
      setDataText('[]')
      setTableData([])
      setIsInitialized(false)
      form.resetFields()
      
      // 清空全局变量
      window.lastSelectedChartType = ''
      console.log('清空specText，清空lastSelectedChartType')
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
      bar: { 
        xField: 'x', yField: 'y', colorField: '',
        xType: 'ordinal', yType: 'quantitative', colorType: 'nominal'
      },
      line: { 
        xField: 'x', yField: 'y', colorField: '',
        xType: 'ordinal', yType: 'quantitative', colorType: 'nominal'
      },
      scatter: { 
        xField: 'x', yField: 'y', colorField: '',
        xType: 'quantitative', yType: 'quantitative', colorType: 'nominal'
      },
      bubble: { 
        xField: 'x', yField: 'y', colorField: '', sizeField: 'size',
        xType: 'quantitative', yType: 'quantitative', colorType: 'nominal', sizeType: 'quantitative'
      },
      pie: { 
        categoryField: 'category', valueField: 'value',
        categoryType: 'nominal', valueType: 'quantitative'
      },
      heatmap: { 
        xField: 'x', yField: 'y', valueField: 'value',
        xType: 'ordinal', yType: 'ordinal', valueType: 'quantitative'
      },
      treemap: { 
        categoryField: 'category', sizeField: 'size', colorField: 'category',
        categoryType: 'nominal', sizeType: 'quantitative', colorType: 'nominal'
      },
      chord: { 
        sourceField: 'source', targetField: 'target', valueField: 'value',
        sourceType: 'nominal', targetType: 'nominal', valueType: 'quantitative'
      },
      funnel: { 
        stageField: 'stage', valueField: 'value', rateField: 'rate',
        stageType: 'ordinal', valueType: 'quantitative', rateType: 'quantitative'
      },
      nodelink: { 
        nodeField: 'node', xField: 'x', yField: 'y', groupField: 'group', sizeField: 'size', sourceField: 'source', targetField: 'target',
        nodeType: 'nominal', xType: 'quantitative', yType: 'quantitative', groupType: 'nominal', sizeType: 'quantitative', sourceType: 'nominal', targetType: 'nominal'
      }
    }
    return CHART_CONFIGS[chartType] || CHART_CONFIGS.bar
  }





  const handleCreateNewChart = (chartType) => {
    console.log('创建新图表:', chartType)
    
    // 重置所有状态
    setChartType(chartType)
    setFormValues({})
    setDataText('[]')
    setTableData([])
    setIsInitialized(false)
    
    // 获取默认数据和配置
    const defaultData = getDefaultData(chartType)
    const defaultConfig = getDefaultConfig(chartType)
    
    // 设置默认值
    const resetValues = {
      chartType: chartType,
      title: '',
      description: '',
      width: undefined,
      height: undefined,
      opacity: 1.0,
      strokeWidth: 0,
      cornerRadius: 0,
      pointSize: undefined,
      strokeDash: [],
      innerRadius: undefined,
      showLegend: true,
      showGrid: true,
      legendPosition: 'right',
      legendOrientation: 'vertical',
      fontFamily: '',
      fontSize: undefined,
      dataText: JSON.stringify(defaultData, null, 2),
      ...defaultConfig
    }
    
    // 设置表单值和状态
    setDataText(JSON.stringify(defaultData, null, 2))
    setTableData(defaultData)
    setIsInitialized(true)
    
    // 重置表单并设置新值
    form.resetFields()
    setTimeout(() => {
      form.setFieldsValue(resetValues)
      setFormValues(resetValues)
    }, 0)
    
    // 更新全局变量，防止重复触发
    window.lastSelectedChartType = chartType
    console.log('创建新图表后，更新lastSelectedChartType:', chartType)
    
    message.info(`已创建新的${getChartTypeLabel(chartType)}`)
  }

  const handleSave = async () => {
    try {
      // 生成当前的ECharts配置
      const currentFormValues = form.getFieldsValue()
      const currentDataValues = tableData && tableData.length > 0 ? tableData : (safeParseJSON(dataText) || [])
      
      const config = {
        chartType,
        title: currentFormValues.title,
        description: currentFormValues.description,
        width: currentFormValues.width,
        height: currentFormValues.height,
        formValues: currentFormValues,
        dataValues: currentDataValues
      }
      
      const specText = JSON.stringify(config, null, 2)
      
      // 尝试获取ECharts实例的截图
      let dataUrl = ''
      const container = embedContainerRef.current
      if (container) {
        const canvas = container.querySelector('canvas')
        if (canvas && typeof canvas.toDataURL === 'function') {
          dataUrl = canvas.toDataURL('image/png')
        }
      }
      
      // 保存包含完整配置的图表
      onSave?.({ specText, thumbDataUrl: dataUrl })
    } catch (e) {
      console.error('保存图表时出错:', e)
      onSave?.({ specText: '', thumbDataUrl: '' })
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', width: '100%', minWidth: 0, gap: 16 }}>
      <Space align="center" style={{ justifyContent: 'space-between', marginBottom: 8 }}>
        <Title level={5} style={{ marginTop: 0, marginBottom: 0 }}>ECharts 图表编辑器</Title>
        <Button type="primary" size="small" onClick={handleSave}>保存到历史</Button>
      </Space>

      <Form
        form={form}
        // layout="vertical"
        layout="horizontal"
        initialValues={{
          chartType: '',
          dataText: '[]',
          title: '',
          description: '',
          width: undefined,
          height: undefined,
          opacity: 1.0,
          strokeWidth: 0,
          cornerRadius: 0,
          pointSize: undefined,
          strokeDash: [],
          innerRadius: undefined,
          showLegend: true,
          showGrid: true,
          legendPosition: 'right',
          legendOrientation: 'vertical',
          fontFamily: '',
          fontSize: undefined
        }}
        onValuesChange={(changed, all) => {
          // 设置内部更新标志
          isInternalUpdate.current = true
          
          // 处理图表类型变化 - 无论是否相同类型都重新创建
          if ('chartType' in changed) {
            const next = changed.chartType
            console.log('onValuesChange - chartType changed:', { next, previous: chartType })
            if (next) {
              setChartType(next)
              const defaultData = getDefaultData(next)
              setDataText(JSON.stringify(defaultData, null, 2))
              setTableData(defaultData) // 同时设置表格数据
              setIsInitialized(true)
              
              // 根据图表类型设置默认字段配置
              const defaultConfig = getDefaultConfig(next)
              
              // 重置所有字段为默认值，而不是保留之前的值
              const resetValues = {
                // 基础配置
                title: '',
                description: '',
                width: undefined,
                height: undefined,
                
                // 样式配置 - 重置为默认值
                opacity: 1.0,
                strokeWidth: 0,
                cornerRadius: 0,
                pointSize: undefined,
                strokeDash: [],
                innerRadius: undefined,
                showLegend: true,
                showGrid: true,
                legendPosition: 'right',
                legendOrientation: 'vertical',
                fontFamily: '',
                fontSize: undefined,
                
                // 数据
                dataText: JSON.stringify(defaultData, null, 2),
                
                // 字段配置 - 使用图表类型的默认配置
                ...defaultConfig
              }
              
              // 设置表单值和状态
              setTimeout(() => {
                form.setFieldsValue(resetValues)
                setFormValues(resetValues)
                isInternalUpdate.current = false
              }, 0)
            } else {
              // 如果清空了图表类型，重置状态
              setChartType('')
              setFormValues({})
              setDataText('[]')
              setTableData([])
              setIsInitialized(false)
              isInternalUpdate.current = false
            }
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
              onOpenChange={(open) => {
                // 当下拉框打开时，记录当前值
                if (open) {
                  const currentValue = form.getFieldValue('chartType')
                  console.log('下拉框打开，记录当前值:', currentValue)
                  // 存储当前值，用于后续检测重复选择
                  window.lastSelectedChartType = currentValue
                }
              }}
              onSelect={(value, option) => {
                // 使用onSelect事件，这个事件在选择选项时触发
                const lastValue = window.lastSelectedChartType
                console.log('Select onSelect:', { value, lastValue, isRepeat: value === lastValue })
                
                if (value && lastValue && value === lastValue) {
                  // 重复选择相同类型，视为新建图表
                  console.log('重复选择相同类型，视为新建图表')
                  handleCreateNewChart(value)
                }
              }}
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