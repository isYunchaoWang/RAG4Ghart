import React, { useMemo } from 'react'
import EChartsBase from './EChartsBase'
import { adaptStyleConfig } from './EChartsDataAdapter'

function EChartsLineChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
  const option = useMemo(() => {
    // 检查数据是否为空
    if (!Array.isArray(dataValues) || dataValues.length === 0) {
      return {
        title: {
          text: title || '',
          left: 'center'
        },
        series: [{
          type: 'line',
          data: []
        }]
      }
    }

    const styleConfig = adaptStyleConfig('line', formValues)

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
        trigger: 'axis'
      },
      legend: {
        data: ['Value'],
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
        type: 'category',
        data: dataValues.map(item => item[formValues.xField || 'x'] || ''),
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
        name: 'Value',
        type: 'line',
        data: dataValues.map(item => item[formValues.yField || 'y'] || 0),
        lineStyle: {
          width: formValues.lineWidth || 2,
          opacity: styleConfig.opacity || 0.8
        },
        itemStyle: {
          opacity: styleConfig.opacity || 0.8
        },
        symbol: 'circle',
        symbolSize: formValues.pointSize || 6,
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

export default EChartsLineChart 