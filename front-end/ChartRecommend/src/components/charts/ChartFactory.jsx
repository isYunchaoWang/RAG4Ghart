import React from 'react'
import { VegaEmbed } from 'react-vega'
import BarChart from './BarChart'
import LineChart from './LineChart'
import PieChart from './PieChart'
import ScatterChart from './ScatterChart'
import BubbleChart from './BubbleChart'
import HeatmapChart from './HeatmapChart'
import AreaChart from './AreaChart'

import GenericChart from './GenericChart'

// 图表类型到组件的映射
const CHART_COMPONENTS = {
  // 柱状图
  bar: BarChart,
  
  // 线图
  line: LineChart,
  
  // 饼图
  pie: PieChart,
  
  // 散点图
  scatter: ScatterChart,
  
  // 气泡图
  bubble: BubbleChart,
  
  // 热力图（用于树状图）
  heatmap: HeatmapChart,
  
  // 树状图（使用热力图组件）
  treemap: HeatmapChart,
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
