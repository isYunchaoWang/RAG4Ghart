import React, { useMemo } from 'react'
import EChartsBase from './EChartsBase'
import { adaptStyleConfig, getDefaultColors } from './EChartsDataAdapter'

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
    const colors = getDefaultColors('pie')

    return {
      color: colors,
      title: {
        show: false
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#d9d9d9',
        textStyle: {
          color: '#262626'
        }
      },
      legend: {
        orient: formValues.legendOrientation || 'vertical',
        left: formValues.legendPosition === 'left' ? 'left' : 'right',
        textStyle: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial',
          color: '#262626'
        }
      },
      series: [{
        name: 'Data',
        type: 'pie',
        radius: formValues.innerRadius ? [`${formValues.innerRadius}%`, '80%'] : '100%',
        center: ['50%', '50%'],
        data: dataValues.map((item, index) => ({
          name: item[formValues.categoryField || 'category'] || '',
          value: item[formValues.valueField || 'value'] || 0,
          itemStyle: {
            color: colors[index % colors.length]
          }
        })),
        itemStyle: {
          opacity: styleConfig.opacity || 0.8,
          borderWidth: 2,
          borderColor: '#fff'
        },
        label: {
          show: true,
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial',
          color: '#262626'
        },
        emphasis: {
          itemStyle: {
            opacity: Math.min((styleConfig.opacity || 0.8) + 0.2, 1),
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.1)'
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