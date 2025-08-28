import React from 'react'
import { VegaEmbed } from 'react-vega'
import BarChart from './BarChart'
import LineChart from './LineChart'
import PieChart from './PieChart'
import ScatterChart from './ScatterChart'
import HeatmapChart from './HeatmapChart'
import AreaChart from './AreaChart'
import BoxChart from './BoxChart'
import GenericChart from './GenericChart'

// 图表类型到组件的映射
const CHART_COMPONENTS = {
  // 柱状图系列
  bar: BarChart,
  stacked_bar: BarChart,
  
  // 线图系列
  line: LineChart,
  radar: LineChart,
  
  // 饼图系列
  pie: PieChart,
  sunburst: PieChart,
  
  // 散点图系列
  point: ScatterChart,
  scatter: ScatterChart,
  bubble: ScatterChart,
  fill_bubble: ScatterChart,
  
  // 热力图
  heatmap: HeatmapChart,
  
  // 面积图系列
  stacked_area: AreaChart,
  stream: AreaChart,
  ridgeline: AreaChart,
  violin: AreaChart,
  
  // 箱线图
  box: BoxChart,
  
  // 树状图系列（使用热力图组件）
  treemap: HeatmapChart,
  treemap_D3: HeatmapChart,
  
  // 桑基图（使用热力图组件）
  sankey: HeatmapChart,
}

// 默认图表组件（当找不到对应组件时使用）
const DefaultChart = ({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) => {
  // 如果有图表类型，使用通用图表组件
  if (chartType) {
    return <GenericChart 
      chartType={chartType}
      title={title}
      description={description}
      width={width}
      height={height}
      formValues={formValues}
      dataValues={dataValues}
      onEmbed={onEmbed}
    />
  }
  
  // 否则显示提示信息
  const spec = {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    description: description || undefined,
    title: title || undefined,
    width: width || 180,
    height: height || undefined,
    data: { values: Array.isArray(dataValues) ? dataValues : [] },
    mark: 'text',
    encoding: {
      text: { value: '该图表类型暂不支持' }
    }
  }

  const embedOptions = { actions: false, mode: 'vega-lite' }

  return (
    <VegaEmbed 
      spec={spec} 
      options={embedOptions} 
      style={{ width: '100%', height: '100%' }} 
      onEmbed={onEmbed} 
    />
  )
}

function ChartFactory({ chartType, ...props }) {
  const ChartComponent = CHART_COMPONENTS[chartType] || DefaultChart
  
  return <ChartComponent chartType={chartType} {...props} />
}

export default ChartFactory
