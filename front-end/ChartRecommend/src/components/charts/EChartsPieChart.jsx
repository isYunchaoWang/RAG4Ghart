import React, { useMemo } from 'react'
import EChartsBase from './EChartsBase'
import { adaptStyleConfig } from './EChartsDataAdapter'

function EChartsPieChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
  const option = useMemo(() => {
    // 检查数据是否为空
    if (!Array.isArray(dataValues) || dataValues.length === 0) {
      return {
        title: {
          text: title || '',
          left: 'center'
        },
        series: [{
          type: 'pie',
          data: []
        }]
      }
    }

    const styleConfig = adaptStyleConfig('pie', formValues)

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
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: formValues.legendOrientation || 'vertical',
        left: formValues.legendPosition === 'left' ? 'left' : 'right',
        textStyle: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
        }
      },
      series: [{
        name: 'Data',
        type: 'pie',
        radius: formValues.innerRadius ? [`${formValues.innerRadius}%`, '70%'] : '50%',
        center: ['50%', '50%'],
        data: dataValues.map(item => ({
          name: item[formValues.categoryField || 'category'] || '',
          value: item[formValues.valueField || 'value'] || 0
        })),
        itemStyle: {
          opacity: styleConfig.opacity || 0.8
        },
        label: {
          show: true,
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
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

export default EChartsPieChart 