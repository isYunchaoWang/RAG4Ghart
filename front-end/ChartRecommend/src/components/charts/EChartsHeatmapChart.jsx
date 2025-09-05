import React, { useMemo } from 'react'
import EChartsBase from './EChartsBase'
import { adaptStyleConfig } from './EChartsDataAdapter'

function EChartsHeatmapChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
  const option = useMemo(() => {
    // 检查数据是否为空
    if (!Array.isArray(dataValues) || dataValues.length === 0) {
      return {
        title: {
          text: title || '',
          left: 'center'
        },
        series: [{
          type: 'heatmap',
          data: []
        }]
      }
    }

    const styleConfig = adaptStyleConfig('heatmap', formValues)

    // 处理热力图数据
    const xAxisData = [...new Set(dataValues.map(item => item[formValues.xField || 'x']))]
    const yAxisData = [...new Set(dataValues.map(item => item[formValues.yField || 'y']))]
    
    const heatmapData = dataValues.map(item => [
      xAxisData.indexOf(item[formValues.xField || 'x']),
      yAxisData.indexOf(item[formValues.yField || 'y']),
      item[formValues.valueField || 'value'] || 0
    ])

    // 安全计算min和max值
    const values = dataValues.map(item => item[formValues.valueField || 'value']).filter(val => val !== undefined && val !== null && !isNaN(val))
    const min = values.length > 0 ? Math.min(...values) : 0
    const max = values.length > 0 ? Math.max(...values) : 1

    return {
      title: {
        text: title || '',
        left: 'center',
        textStyle: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
        }
      },
      tooltip: {
        position: 'top',
        formatter: function(params) {
          return `${xAxisData[params.data[0]]}<br/>${yAxisData[params.data[1]]}<br/>数值: ${params.data[2]}`
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
        show: formValues.showGrid !== false
      },
      xAxis: {
        type: 'category',
        data: xAxisData,
        splitArea: {
          show: true
        },
        axisLabel: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
        }
      },
      yAxis: {
        type: 'category',
        data: yAxisData,
        splitArea: {
          show: true
        },
        axisLabel: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
        }
      },
      visualMap: {
        min: min,
        max: max,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '15%',
        textStyle: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
        },
        inRange: {
          color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffcc', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
        }
      },
      series: [{
        name: '热力图',
        type: 'heatmap',
        data: heatmapData,
        label: {
          show: true,
          fontSize: (styleConfig.fontSize || 12) - 2,
          fontFamily: styleConfig.fontFamily || 'Arial'
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    }
  }, [title, dataValues, formValues])

  return (
    <EChartsBase
      chartType={chartType}
      title={title}
      description={description}
      width={width}
      height={height}
      formValues={formValues}
      dataValues={dataValues}
      onEmbed={onEmbed}
      option={option}
    />
  )
}

export default EChartsHeatmapChart 