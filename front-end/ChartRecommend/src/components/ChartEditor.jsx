import { useEffect, useMemo, useState, useRef } from 'react'
import { Form, Input, Typography, theme, Button, Space, Select, Divider, InputNumber, message } from 'antd'
import { VegaEmbed } from 'react-vega'

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
  { label: '和弦图 chord', value: 'chord' },
  { label: '漏斗图 funnel', value: 'funnel' },
  { label: '热力图 heatmap', value: 'heatmap' },
  { label: '折线图 line', value: 'line' },
  { label: '节点链接图 node_link', value: 'node_link' },
  { label: '平行坐标 parallel', value: 'parallel' },
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
    case 'bubble':
    case 'box':
      return 'boxplot'
    case 'heatmap':
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

function buildSpecFromForm({ chartType, title, description, width, height, xField, xType, yField, yType, aggregate, colorField, colorType, sizeField, dataValues }) {
  const spec = {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    description: description || undefined,
    title: title || undefined,
    width: width || undefined,
    height: height || undefined,
    data: { values: Array.isArray(dataValues) ? dataValues : [] },
    mark: mapChartTypeToVegaMark(chartType || 'bar'),
    encoding: {}
  }

  if (xField) spec.encoding.x = { field: xField, type: xType || 'ordinal' }
  if (yField) spec.encoding.y = { field: yField, type: yType || 'quantitative' }

  if (aggregate && yField) {
    spec.encoding.y = {
      ...(spec.encoding.y || {}),
      aggregate: aggregate,
    }
  }

  if (colorField) {
    spec.encoding.color = { field: colorField, type: colorType || 'nominal' }
  }

  if ((chartType === 'bubble' || chartType === 'fill_bubble' || chartType === 'point') && sizeField) {
    spec.encoding.size = { field: sizeField, type: 'quantitative' }
  }

  return spec
}

function pickFormFromSpec(spec) {
  if (!spec) return null
  try {
    const chartType = typeof spec.mark === 'string' ? spec.mark : spec.mark?.type || 'bar'
    const x = spec.encoding?.x || {}
    const y = spec.encoding?.y || {}
    const color = spec.encoding?.color || {}
    const size = spec.encoding?.size || {}
    return {
      chartType,
      title: spec.title || '',
      description: spec.description || '',
      width: spec.width || undefined,
      height: spec.height || undefined,
      xField: x.field || '',
      xType: x.type || undefined,
      yField: y.field || '',
      yType: y.type || undefined,
      aggregate: y.aggregate || '',
      colorField: color.field || '',
      colorType: color.type || undefined,
      sizeField: size.field || '',
      dataText: JSON.stringify(spec.data?.values ?? [], null, 2),
    }
  } catch {
    return null
  }
}

function getDefaultData(chartType) {
  switch (chartType) {
    case 'line':
      return [
        { x: 'A', y: 28 }, { x: 'B', y: 55 }, { x: 'C', y: 43 }, { x: 'D', y: 91 }
      ]
    case 'point':
    case 'bubble':
    case 'fill_bubble':
      return [
        { x: 5, y: 3, size: 10 }, { x: 10, y: 17, size: 30 }, { x: 15, y: 4, size: 15 }, { x: 20, y: 20, size: 45 }
      ]
    case 'heatmap':
      return [
        { x: 'A', y: 'K', value: 10 }, { x: 'A', y: 'L', value: 20 }, { x: 'B', y: 'K', value: 5 }, { x: 'B', y: 'L', value: 15 }
      ]
    case 'bar':
    case 'box':
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

  // 内部受控的表单状态（用 AntD Form 管理）
  const [chartType, setChartType] = useState('bar')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [width, setWidth] = useState()
  const [height, setHeight] = useState()
  const [xField, setXField] = useState('x')
  const [xType, setXType] = useState('ordinal')
  const [yField, setYField] = useState('y')
  const [yType, setYType] = useState('quantitative')
  const [aggregate, setAggregate] = useState('')
  const [colorField, setColorField] = useState('')
  const [colorType, setColorType] = useState('nominal')
  const [sizeField, setSizeField] = useState('')
  const [dataText, setDataText] = useState(JSON.stringify(getDefaultData('bar'), null, 2))

  // 保存 Vega view 与容器引用以便截图
  const viewRef = useRef(null)
  const embedContainerRef = useRef(null)

  // 当外部 specText 变化（例如从历史选中），尝试反填表单
  useEffect(() => {
    const spec = safeParseJSON(specText)
    const mapped = pickFormFromSpec(spec)
    if (mapped) {
      setChartType(mapped.chartType || 'bar')
      setTitle(mapped.title || '')
      setDescription(mapped.description || '')
      setWidth(mapped.width)
      setHeight(mapped.height)
      setXField(mapped.xField || 'x')
      setXType(mapped.xType || 'ordinal')
      setYField(mapped.yField || 'y')
      setYType(mapped.yType || 'quantitative')
      setAggregate(mapped.aggregate || '')
      setColorField(mapped.colorField || '')
      setColorType(mapped.colorType || 'nominal')
      setSizeField(mapped.sizeField || '')
      setDataText(mapped.dataText || JSON.stringify(getDefaultData(mapped.chartType || 'bar'), null, 2))
      form.setFieldsValue({
        chartType: mapped.chartType,
        title: mapped.title,
        description: mapped.description,
        width: mapped.width,
        height: mapped.height,
        xField: mapped.xField,
        xType: mapped.xType,
        yField: mapped.yField,
        yType: mapped.yType,
        aggregate: mapped.aggregate,
        colorField: mapped.colorField,
        colorType: mapped.colorType,
        sizeField: mapped.sizeField,
        dataText: mapped.dataText,
      })
    }
  }, [specText])

  // 基于表单字段构建规范
  const dataValues = useMemo(() => {
    const parsed = safeParseJSON(dataText)
    return Array.isArray(parsed) ? parsed : []
  }, [dataText])

  const liveSpec = useMemo(() => {
    return buildSpecFromForm({ chartType, title, description, width, height, xField, xType, yField, yType, aggregate, colorField, colorType, sizeField, dataValues })
  }, [chartType, title, description, width, height, xField, xType, yField, yType, aggregate, colorField, colorType, sizeField, dataValues])

  // 同步到外部 specText
  useEffect(() => {
    onChange?.(JSON.stringify(liveSpec, null, 2))
  }, [liveSpec])

  const embedOptions = { actions: false, mode: 'vega-lite' }

  const isBubbleLike = chartType === 'bubble' || chartType === 'fill_bubble' || chartType === 'point'
  const isHeatmap = chartType === 'heatmap'

  const handleSave = async () => {
    const specStr = JSON.stringify(liveSpec, null, 2)
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
      onSave?.({ specText: specStr, thumbDataUrl: dataUrl })
    } catch (e) {
      onSave?.({ specText: specStr, thumbDataUrl: '' })
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
          chartType: 'bar', xField: 'x', xType: 'ordinal', yField: 'y', yType: 'quantitative', aggregate: '', dataText
        }}
        onValuesChange={(changed, all) => {
          if ('chartType' in changed) {
            const next = changed.chartType
            setChartType(next)
            // 如果当前数据字段仍为默认 x/y，自动切换默认数据
            setDataText(JSON.stringify(getDefaultData(next), null, 2))
            if (next === 'point' || next === 'bubble' || next === 'fill_bubble') {
              setXType('quantitative'); setYType('quantitative');
              form.setFieldsValue({ xType: 'quantitative', yType: 'quantitative' })
              setSizeField('size');
              form.setFieldsValue({ sizeField: 'size' })
            } else if (next === 'heatmap') {
              setXType('ordinal'); setYType('ordinal');
              form.setFieldsValue({ xType: 'ordinal', yType: 'ordinal' })
              setColorType('quantitative');
              form.setFieldsValue({ colorType: 'quantitative' })
            } else {
              setXType('ordinal'); setYType('quantitative');
              form.setFieldsValue({ xType: 'ordinal', yType: 'quantitative' })
              setSizeField('');
              form.setFieldsValue({ sizeField: '' })
              setColorType('nominal');
              form.setFieldsValue({ colorType: 'nominal' })
            }
          }
          if ('title' in changed) setTitle(all.title)
          if ('description' in changed) setDescription(all.description)
          if ('width' in changed) setWidth(all.width)
          if ('height' in changed) setHeight(all.height)
          if ('xField' in changed) setXField(all.xField)
          if ('xType' in changed) setXType(all.xType)
          if ('yField' in changed) setYField(all.yField)
          if ('yType' in changed) setYType(all.yType)
          if ('aggregate' in changed) setAggregate(all.aggregate)
          if ('colorField' in changed) setColorField(all.colorField)
          if ('colorType' in changed) setColorType(all.colorType)
          if ('sizeField' in changed) setSizeField(all.sizeField)
          if ('dataText' in changed) setDataText(all.dataText)
        }}
      >
        <Space size={12} wrap>
          <Form.Item label="图表类型" name="chartType" style={{ minWidth: 160 }}>
            <Select options={CHART_TYPES} />
          </Form.Item>
          <Form.Item label="标题" name="title" style={{ minWidth: 240 }}>
            <Input placeholder="可选" />
          </Form.Item>
          <Form.Item label="描述" name="description" style={{ minWidth: 300 }}>
            <Input placeholder="可选" />
          </Form.Item>
          <Form.Item label="宽度" name="width">
            <InputNumber min={0} style={{ width: 120 }} placeholder="auto" />
          </Form.Item>
          <Form.Item label="高度" name="height">
            <InputNumber min={0} style={{ width: 120 }} placeholder="auto" />
          </Form.Item>
        </Space>

        <Divider style={{ margin: '8px 0' }} />

        <Space size={12} wrap>
          <Form.Item label="X 字段" name="xField">
            <Input style={{ width: 160 }} />
          </Form.Item>
          <Form.Item label="X 类型" name="xType">
            <Select options={FIELD_TYPES} style={{ width: 180 }} />
          </Form.Item>
          <Form.Item label="Y 字段" name="yField">
            <Input style={{ width: 160 }} />
          </Form.Item>
          <Form.Item label="Y 类型" name="yType">
            <Select options={FIELD_TYPES} style={{ width: 180 }} />
          </Form.Item>
          <Form.Item label="聚合" name="aggregate">
            <Select options={AGG_FUNCS} style={{ width: 160 }} />
          </Form.Item>
          <Form.Item label="颜色字段" name="colorField">
            <Input style={{ width: 160 }} placeholder="可选" />
          </Form.Item>
          {isHeatmap && (
            <Form.Item label="颜色类型" name="colorType">
              <Select options={COLOR_TYPES} style={{ width: 180 }} />
            </Form.Item>
          )}
          {isBubbleLike && (
            <Form.Item label="大小字段" name="sizeField">
              <Input style={{ width: 160 }} placeholder="例如：size" />
            </Form.Item>
          )}
        </Space>

        <Form.Item label="数据（JSON 数组）" name="dataText">
          <Input.TextArea autoSize={{ minRows: 6, maxRows: 12 }} placeholder='例如:[{"x":"A","y":10}]' />
        </Form.Item>
      </Form>

      <div ref={embedContainerRef} style={{ flex: 1, minHeight: 200, border: `1px dashed ${token.colorBorder}`, borderRadius: 8, display: 'flex', alignItems: 'stretch', justifyContent: 'stretch', padding: 8, overflow: 'hidden' }}>
        <VegaEmbed spec={liveSpec} options={embedOptions} style={{ width: '100%', height: '100%' }} onNewView={(view) => { viewRef.current = view }} />
      </div>
    </div>
  )
}

export default ChartEditor 