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
  { label: 'Bar Chart', value: 'bar' },
  { label: 'Bubble Chart', value: 'bubble' },
  { label: 'Chord Chart', value: 'chord' },
  { label: 'Funnel Chart', value: 'funnel' },
  { label: 'Line Chart', value: 'line' },
  { label: 'Node-Link Chart', value: 'nodelink' },
  { label: 'Pie Chart', value: 'pie' },
  { label: 'Scatter Chart', value: 'scatter' },
  { label: 'Treemap Chart', value: 'treemap' },
]

// Get chart type label
const getChartTypeLabel = (chartType) => {
  const chartTypeObj = CHART_TYPES.find(item => item.value === chartType)
  return chartTypeObj ? chartTypeObj.label.split(' ')[0] : chartType
}

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
  // Reverse mapping: map from Vega-Lite mark type back to our chart type
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
    
    // Basic information
    const result = {
      chartType,
      title: spec.title || '',
      description: spec.description || '',
      width: spec.width || undefined,
      height: spec.height || undefined,
      dataText: JSON.stringify(spec.data?.values ?? [], null, 2),
    }
    
    // Extract style configuration
    if (mark.opacity !== undefined) result.opacity = mark.opacity
    if (mark.strokeWidth !== undefined) result.strokeWidth = mark.strokeWidth
    if (mark.cornerRadius !== undefined) result.cornerRadius = mark.cornerRadius
    if (mark.size !== undefined) result.pointSize = mark.size
    if (mark.strokeDash) result.strokeDash = mark.strokeDash
    if (mark.innerRadius !== undefined) result.innerRadius = mark.innerRadius
    
    // Extract configuration information
    const config = spec.config || {}
    if (config.axis) {
      if (config.axis.grid === false) result.showGrid = false
    }
    if (config.legend) {
      if (config.legend.disable) result.showLegend = false
      if (config.legend.orient) result.legendPosition = config.legend.orient
      if (config.legend.direction) result.legendOrientation = config.legend.direction
    }
    
    // Extract font configuration
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

    
    // Extract field information based on encoding
    Object.entries(encoding).forEach(([key, value]) => {
      if (value && value.field) {
        // Map vega encoding to our field names
        let fieldName = key
        if (key === 'theta') fieldName = 'value' // Map pie chart's theta to value
        
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
        { x: 10, y: 15, category: 'Category A' },
        { x: 20, y: 25, category: 'Category A' },
        { x: 30, y: 35, category: 'Category B' },
        { x: 40, y: 45, category: 'Category B' }
      ]
    case 'bubble':
      return [
        { x: 10, y: 15, size: 20, category: 'Category A' },
        { x: 20, y: 25, size: 35, category: 'Category A' },
        { x: 30, y: 35, size: 50, category: 'Category B' },
        { x: 40, y: 45, size: 65, category: 'Category B' }
      ]
    case 'pie':
      return [
        { category: 'Category A', value: 30 },
        { category: 'Category B', value: 25 },
        { category: 'Category C', value: 20 },
        { category: 'Category D', value: 15 },
        { category: 'Category E', value: 10 }
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
        { category: 'Electronics', size: 300, color: 'Technology' },
        { category: 'Clothing', size: 250, color: 'Fashion' },
        { category: 'Food', size: 200, color: 'Lifestyle' },
        { category: 'Books', size: 150, color: 'Education' },
        { category: 'Home', size: 180, color: 'Lifestyle' },
        { category: 'Sports', size: 120, color: 'Health' },
        { category: 'Beauty', size: 160, color: 'Fashion' },
        { category: 'Automotive', size: 220, color: 'Transportation' },
        { category: 'Gaming', size: 140, color: 'Entertainment' },
        { category: 'Music', size: 90, color: 'Entertainment' }
      ]
    case 'chord':
      return [
        { source: 'Beijing', target: 'Shanghai', value: 25 },
        { source: 'Beijing', target: 'Guangzhou', value: 18 },
        { source: 'Beijing', target: 'Shenzhen', value: 15 },
        { source: 'Beijing', target: 'Hangzhou', value: 12 },
        { source: 'Shanghai', target: 'Guangzhou', value: 22 },
        { source: 'Shanghai', target: 'Shenzhen', value: 20 },
        { source: 'Shanghai', target: 'Hangzhou', value: 28 },
        { source: 'Shanghai', target: 'Nanjing', value: 16 },
        { source: 'Guangzhou', target: 'Shenzhen', value: 30 },
        { source: 'Guangzhou', target: 'Hangzhou', value: 14 },
        { source: 'Guangzhou', target: 'Chengdu', value: 18 },
        { source: 'Shenzhen', target: 'Hangzhou', value: 10 },
        { source: 'Shenzhen', target: 'Chengdu', value: 12 },
        { source: 'Hangzhou', target: 'Nanjing', value: 22 },
        { source: 'Hangzhou', target: 'Chengdu', value: 16 },
        { source: 'Nanjing', target: 'Chengdu', value: 14 },
        { source: 'Nanjing', target: 'Wuhan', value: 20 },
        { source: 'Chengdu', target: 'Wuhan', value: 18 },
        { source: 'Wuhan', target: 'Xian', value: 24 },
        { source: 'Chengdu', target: 'Xian', value: 16 },
        { source: 'Xian', target: 'Beijing', value: 20 }
      ]
    case 'funnel':
      return [
        { stage: 'Visit', value: 1000, rate: 1.0 },
        { stage: 'Register', value: 800, rate: 0.8 },
        { stage: 'Download', value: 600, rate: 0.6 },
        { stage: 'Purchase', value: 200, rate: 0.2 },
        { stage: 'Repurchase', value: 80, rate: 0.08 }
      ]
    case 'nodelink':
      return [
        { node: 'A', x: 10, y: 20, group: 'Group 1', size: 30 },
        { node: 'B', x: 30, y: 40, group: 'Group 1', size: 25 },
        { node: 'C', x: 50, y: 30, group: 'Group 2', size: 35 },
        { node: 'D', x: 70, y: 60, group: 'Group 2', size: 20 },
        { node: 'E', x: 90, y: 10, group: 'Group 3', size: 40 },
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

  // Simplified state management - initial state is empty
  const [chartType, setChartType] = useState('')
  const [formValues, setFormValues] = useState({})
  const [dataText, setDataText] = useState('[]')
  const [tableData, setTableData] = useState([])
  const [isInitialized, setIsInitialized] = useState(false)

  // Save Vega view and container reference for screenshot
  const viewRef = useRef(null)
  const embedContainerRef = useRef(null)

  // Flag to prevent circular updates
  const isUpdatingFromExternal = useRef(false)
  const isInternalUpdate = useRef(false)
  
  // Handle chart type selection from retrieval results
  useEffect(() => {
    if (selectedChartType && selectedChartType !== chartType) {
      console.log('Selected chart type from retrieval results:', selectedChartType)
      handleCreateNewChart(selectedChartType)
    }
  }, [selectedChartType])

  // Only process when valid specText is passed from outside (when selecting from history)
  useEffect(() => {
    // If it is a change caused by internal update, ignore it
    if (isUpdatingFromExternal.current || isInternalUpdate.current) {
      return
    }
    
    // Only process when non-empty specText is passed from outside
    if (specText && specText.trim() && specText !== '{}') {
      const spec = safeParseJSON(specText)
      const mapped = pickFormFromSpec(spec)
      if (mapped && mapped.chartType) {
        setChartType(mapped.chartType)
        setFormValues(mapped)
        setDataText(mapped.dataText || JSON.stringify(getDefaultData(mapped.chartType), null, 2))
        
        // Parse data and set to table
        try {
          const parsedData = JSON.parse(mapped.dataText || '[]')
          setTableData(Array.isArray(parsedData) ? parsedData : [])
        } catch {
          setTableData([])
        }
        
        setIsInitialized(true)
        form.setFieldsValue(mapped)
        
        // Update global variable to detect duplicate selection
        window.lastSelectedChartType = mapped.chartType
        console.log('Loaded from history, updating lastSelectedChartType:', mapped.chartType)
      }
    } else if (!specText || specText.trim() === '' || specText === '{}') {
      // If external cleared specText, reset state
      setChartType('')
      setFormValues({})
      setDataText('[]')
      setTableData([])
      setIsInitialized(false)
      form.resetFields()
      
      // Clear global variable
      window.lastSelectedChartType = ''
      console.log('Cleared specText, cleared lastSelectedChartType')
    }
  }, [specText, form])

  // Build specification based on form fields
  const dataValues = useMemo(() => {
    // Prioritize table data, use JSON data if not available
    if (tableData && tableData.length > 0) {
      return tableData
    }
    const parsed = safeParseJSON(dataText)
    return Array.isArray(parsed) ? parsed : []
  }, [tableData, dataText])

  // Sync to external specText - now handled by each chart component
  useEffect(() => {
    // Only sync after user has selected chart type
    if (chartType && !isUpdatingFromExternal.current) {
      isUpdatingFromExternal.current = true
      // Sync logic can be added here if needed
      setTimeout(() => {
        isUpdatingFromExternal.current = false
      }, 100)
    }
  }, [chartType])

  // Helper function to get default configuration
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
    console.log('Creating new chart:', chartType)
    
    // Reset all states
    setChartType(chartType)
    setFormValues({})
    setDataText('[]')
    setTableData([])
    setIsInitialized(false)
    
    // Get default data and configuration
    const defaultData = getDefaultData(chartType)
    const defaultConfig = getDefaultConfig(chartType)
    
    // Set default values
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
    
    // Set form values and state
    setDataText(JSON.stringify(defaultData, null, 2))
    setTableData(defaultData)
    setIsInitialized(true)
    
    // Reset form and set new values
    form.resetFields()
    setTimeout(() => {
      form.setFieldsValue(resetValues)
      setFormValues(resetValues)
    }, 0)
    
    // Update global variable to prevent duplicate triggering
    window.lastSelectedChartType = chartType
    console.log('After creating new chart, updating lastSelectedChartType:', chartType)
    
    message.info(`Created new ${getChartTypeLabel(chartType)}`)
  }

  const handleSave = async () => {
    try {
      // Generate current ECharts configuration
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
      
      // Try to get screenshot of ECharts instance
      let dataUrl = ''
      const container = embedContainerRef.current
      if (container) {
        const canvas = container.querySelector('canvas')
        if (canvas && typeof canvas.toDataURL === 'function') {
          dataUrl = canvas.toDataURL('image/png')
        }
      }
      
      // Save chart with complete configuration
      onSave?.({ specText, thumbDataUrl: dataUrl })
    } catch (e) {
      console.error('Error saving chart:', e)
      onSave?.({ specText: '', thumbDataUrl: '' })
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', width: '100%', minWidth: 0, gap: 16 }}>
      <Space align="center" style={{ justifyContent: 'space-between', marginBottom: 8 }}>
        <Title level={5} style={{ marginTop: 0, marginBottom: 0 }}>Chart Editor</Title>
        <Button type="primary" size="small" onClick={handleSave}>Save to History</Button>
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
          // Set internal update flag
          isInternalUpdate.current = true
          
          // Handle chart type changes - recreate regardless of same type
          if ('chartType' in changed) {
            const next = changed.chartType
            console.log('onValuesChange - chartType changed:', { next, previous: chartType })
            if (next) {
              setChartType(next)
              const defaultData = getDefaultData(next)
              setDataText(JSON.stringify(defaultData, null, 2))
              setTableData(defaultData) // Also set table data
              setIsInitialized(true)
              
              // Set default field configuration based on chart type
              const defaultConfig = getDefaultConfig(next)
              
              // Reset all fields to default values instead of keeping previous values
              const resetValues = {
                // Basic configuration
                title: '',
                description: '',
                width: undefined,
                height: undefined,
                
                // Style configuration - reset to default values
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
                
                // Data
                dataText: JSON.stringify(defaultData, null, 2),
                
                // Field configuration - use chart type default configuration
                ...defaultConfig
              }
              
              // Set form values and state
              setTimeout(() => {
                form.setFieldsValue(resetValues)
                setFormValues(resetValues)
                isInternalUpdate.current = false
              }, 0)
            } else {
              // If chart type is cleared, reset state
              setChartType('')
              setFormValues({})
              setDataText('[]')
              setTableData([])
              setIsInitialized(false)
              isInternalUpdate.current = false
            }
          } else {
            // Other field changes
            setFormValues(all)
            
            // Handle data text changes
            if ('dataText' in changed) {
              setDataText(all.dataText)
            }
            
            setTimeout(() => {
              isInternalUpdate.current = false
            }, 0)
          }
        }}
      >
        {/* Basic Configuration */}
        <Space size={12} wrap style={{ marginBottom: 16 }}>
          <Form.Item label="Chart Type" name="chartType" style={{ minWidth: 160, marginBottom: 12 }}>
            <Select 
              id="chartType"
              options={CHART_TYPES} 
              placeholder="Please select chart type"
              allowClear
              onOpenChange={(open) => {
                // When dropdown opens, record current value
                if (open) {
                  const currentValue = form.getFieldValue('chartType')
                  console.log('Dropdown opened, recording current value:', currentValue)
                  // Store current value for subsequent duplicate selection detection
                  window.lastSelectedChartType = currentValue
                }
              }}
              onSelect={(value, option) => {
                // Use onSelect event, which triggers when selecting an option
                const lastValue = window.lastSelectedChartType
                console.log('Select onSelect:', { value, lastValue, isRepeat: value === lastValue })
                
                if (value && lastValue && value === lastValue) {
                  // Repeated selection of same type, treat as new chart creation
                  console.log('Repeated selection of same type, treat as new chart creation')
                  handleCreateNewChart(value)
                }
              }}
            />
          </Form.Item>
          
          {chartType && (
            <>
              <Form.Item label="Title" name="title" style={{ minWidth: 200, marginBottom: 12 }}>
                <Input id="title" placeholder="Optional" />
              </Form.Item>
              <Form.Item label="Description" name="description" style={{ minWidth: 250, marginBottom: 12 }}>
                <Input id="description" placeholder="Optional" />
              </Form.Item>
              <Form.Item label="Width" name="width" style={{ marginBottom: 12 }}>
                <InputNumber id="width" min={0} style={{ width: 100 }} placeholder="auto" />
              </Form.Item>
              <Form.Item label="Height" name="height" style={{ marginBottom: 12 }}>
                <InputNumber id="height" min={0} style={{ width: 100 }} placeholder="auto" />
              </Form.Item>
            </>
          )}
        </Space>

        {/* Only show dynamic configuration when chart type is selected */}
        {chartType && (
          <div style={{ display: 'flex', gap: '16px', marginTop: '16px' }}>
            {/* Left: Field configuration and style configuration */}
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

            {/* Middle divider */}
            <Divider type="vertical" style={{ height: 'auto', margin: '0 4px' }} />

            {/* Right: Data input */}
            <div style={{ flex: 1 }}>
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: '14px', fontWeight: 500, marginBottom: 12, color: '#262626' }}>
                  JSON Data Editor
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
            Please select a chart type to start configuration
          </div>
        )}
      </div>
    </div>
  )
}

export default ChartEditor       