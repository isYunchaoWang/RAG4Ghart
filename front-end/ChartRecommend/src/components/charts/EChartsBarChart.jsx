import React, { useMemo } from 'react'
import EChartsBase from './EChartsBase'
import { adaptStyleConfig, getDefaultColors } from './EChartsDataAdapter'

function EChartsBarChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
  const option = useMemo(() => {
    // 检查数据是否为空
    if (!Array.isArray(dataValues) || dataValues.length === 0) {
      return {
        title: {
          text: title || '',
          left: 'center'
        },
        series: [{
          type: 'bar',
          data: []
        }]
      }
    }

    const styleConfig = adaptStyleConfig('bar', formValues)
    const colors = getDefaultColors('bar')

    return {
      color: colors,
      title: {
        text: title || '',
        left: 'center',
        textStyle: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial',
          color: '#262626'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#d9d9d9',
        textStyle: {
          color: '#262626'
        }
      },
      legend: {
        data: ['Value'],
        orient: formValues.legendOrientation || 'horizontal',
        left: formValues.legendPosition === 'left' ? 'left' : 'right',
        textStyle: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial',
          color: '#262626'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
        show: formValues.showGrid !== false,
        backgroundColor: 'transparent',
        borderColor: '#f0f0f0'
      },
      xAxis: {
        type: 'category',
        data: dataValues.map(item => item[formValues.xField || 'x'] || ''),
        axisLabel: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial',
          color: '#595959'
        },
        axisLine: {
          lineStyle: {
            color: '#d9d9d9'
          }
        }
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial',
          color: '#595959'
        },
        axisLine: {
          lineStyle: {
            color: '#d9d9d9'
          }
        },
        splitLine: {
          lineStyle: {
            color: '#f0f0f0'
          }
        }
      },
      series: [{
        name: 'Value',
        type: 'bar',
        data: dataValues.map((item, index) => ({
          value: item[formValues.yField || 'y'] || 0,
          itemStyle: {
            color: colors[index % colors.length],
            opacity: styleConfig.opacity || 0.8,
            borderRadius: formValues.cornerRadius || 4
          }
        })),
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

export default EChartsBarChart 