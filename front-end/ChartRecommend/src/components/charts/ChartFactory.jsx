import React from 'react'

// ECharts组件
import EChartsBarChart from './EChartsBarChart'
import EChartsLineChart from './EChartsLineChart'
import EChartsPieChart from './EChartsPieChart'
import EChartsScatterChart from './EChartsScatterChart'
import EChartsBubbleChart from './EChartsBubbleChart'
import EChartsHeatmapChart from './EChartsHeatmapChart'
import EChartsChordChart from './EChartsChordChart'
import EChartsFunnelChart from './EChartsFunnelChart'
import EChartsNodeLinkChart from './EChartsNodeLinkChart'

// 图表类型到组件的映射
const CHART_COMPONENTS = {
  // ECharts组件
  bar: EChartsBarChart,
  line: EChartsLineChart,
  pie: EChartsPieChart,
  scatter: EChartsScatterChart,
  bubble: EChartsBubbleChart,
  heatmap: EChartsHeatmapChart,
  treemap: EChartsHeatmapChart,
  chord: EChartsChordChart,
  funnel: EChartsFunnelChart,
  node_link: EChartsNodeLinkChart,
}

// 默认图表组件（当找不到对应组件时使用）
const DefaultChart = ({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) => {
  // 显示提示信息
  return (
    <div style={{ 
      width: '100%', 
      height: '100%', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      color: '#999',
      fontSize: '14px'
    }}>
      该图表类型暂不支持
    </div>
  )
}

function ChartFactory({ chartType, ...props }) {
  const ChartComponent = CHART_COMPONENTS[chartType] || DefaultChart
  
  return <ChartComponent chartType={chartType} {...props} />
}

export default ChartFactory
