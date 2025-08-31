import React, { useMemo } from 'react'
import EChartsBase from './EChartsBase'
import { adaptDataForECharts, adaptStyleConfig } from './EChartsDataAdapter'

function EChartsFunnelChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
  const option = useMemo(() => {
    // 检查数据是否为空
    if (!Array.isArray(dataValues) || dataValues.length === 0) {
      return {
        title: {
          text: title || '',
          left: 'center'
        },
        series: [{
          type: 'funnel',
          data: []
        }]
      }
    }

    const adaptedData = adaptDataForECharts('funnel', dataValues, formValues)
    const styleConfig = adaptStyleConfig('funnel', formValues)

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
        trigger: 'item',
        formatter: function(params) {
          const rate = params.data.rate || 0
          return `${params.data.name}<br/>数值: ${params.data.value}<br/>转化率: ${(rate * 100).toFixed(1)}%`
        }
      },
      legend: {
        data: adaptedData.map(item => item.name),
        orient: formValues.legendOrientation || 'vertical',
        left: formValues.legendPosition === 'left' ? 'left' : 'right',
        textStyle: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
        }
      },
      series: [{
        name: '漏斗图',
        type: 'funnel',
        left: '10%',
        top: 60,
        width: '80%',
        height: '80%',
        min: 0,
        max: Math.max(...adaptedData.map(item => item.value), 1),
        minSize: '0%',
        maxSize: '100%',
        sort: styleConfig.sort,
        gap: styleConfig.gap,
        label: {
          show: true,
          position: 'inside',
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial',
          formatter: function(params) {
            return `${params.data.name}\n${params.data.value}`
          }
        },
        labelLine: {
          length: 10,
          lineStyle: {
            width: 1,
            type: 'solid'
          }
        },
        itemStyle: {
          opacity: styleConfig.opacity || 0.8,
          borderColor: '#fff',
          borderWidth: 1
        },
        emphasis: {
          label: {
            fontSize: (styleConfig.fontSize || 12) + 2
          }
        },
        data: adaptedData
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

export default EChartsFunnelChart 