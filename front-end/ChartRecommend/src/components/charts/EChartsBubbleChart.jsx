import React, { useMemo } from 'react'
import EChartsBase from './EChartsBase'
import { adaptStyleConfig } from './EChartsDataAdapter'

function EChartsBubbleChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
  const option = useMemo(() => {
    // 检查数据是否为空
    if (!Array.isArray(dataValues) || dataValues.length === 0) {
      return {
        title: {
          text: title || '',
          left: 'center'
        },
        series: [{
          type: 'scatter',
          data: []
        }]
      }
    }

    const styleConfig = adaptStyleConfig('bubble', formValues)

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
          return `${params.data[0]}<br/>${params.data[1]}<br/>大小: ${params.data[2]}`
        }
      },
      legend: {
        data: ['气泡'],
        orient: formValues.legendOrientation || 'horizontal',
        left: formValues.legendPosition === 'left' ? 'left' : 'right',
        textStyle: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
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
        type: 'value',
        axisLabel: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
        }
      },
      series: [{
        name: '气泡',
        type: 'scatter',
        data: dataValues.map(item => [
          item[formValues.xField || 'x'] || 0,
          item[formValues.yField || 'y'] || 0,
          item[formValues.sizeField || 'size'] || 20
        ]),
        symbolSize: function(data) {
          return data[2] || 20
        },
        itemStyle: {
          opacity: styleConfig.opacity || 0.8
        },
        emphasis: {
          itemStyle: {
            opacity: Math.min((styleConfig.opacity || 0.8) + 0.2, 1)
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

export default EChartsBubbleChart 