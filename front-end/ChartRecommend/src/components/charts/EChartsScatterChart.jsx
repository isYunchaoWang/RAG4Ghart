import React, { useMemo } from 'react'
import EChartsBase from './EChartsBase'
import { adaptStyleConfig, getDefaultColors } from './EChartsDataAdapter'

function EChartsScatterChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
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

    const styleConfig = adaptStyleConfig('scatter', formValues)
    const colors = getDefaultColors('scatter')

    // 检查是否有color字段来分组数据
    let colorField = formValues.colorField
    
    // 自动检测：如果colorField为空或占位符，但数据中有category字段，则自动使用category
    if ((!colorField || colorField.includes('e.g.:')) && dataValues.length > 0) {
      const firstItem = dataValues[0]
      if (firstItem && firstItem.category) {
        colorField = 'category'
        console.log('Auto-detected category field for scatter chart')
      }
    }
    
    let series = []
    let legendData = []

    // 检查是否有color字段来分组数据，并且不是占位符文本
    if (colorField && colorField.trim() && !colorField.includes('e.g.:')) {
      // 有多组散点的情况 - 按color字段分组
      const groupedData = {}
      
      dataValues.forEach(item => {
        const colorValue = item[colorField] || 'Unknown'
        if (!groupedData[colorValue]) {
          groupedData[colorValue] = []
        }
        
        // 支持size字段来设置散点大小
        const sizeValue = item[formValues.sizeField || 'size']
        const pointData = [
          item[formValues.xField || 'x'] || 0,
          item[formValues.yField || 'y'] || 0
        ]
        
        // 如果有size字段，添加size信息
        if (sizeValue !== undefined && sizeValue !== null) {
          pointData.push(sizeValue)
        }
        
        groupedData[colorValue].push(pointData)
      })

      // 创建多组散点
      Object.keys(groupedData).forEach((colorValue, index) => {
        const color = colors[index % colors.length]
        legendData.push(colorValue)
        
        // 检查是否有size字段
        const hasSizeField = groupedData[colorValue].some(point => point.length > 2)
        
        series.push({
          name: colorValue,
          type: 'scatter',
          data: groupedData[colorValue],
          symbolSize: hasSizeField ? 
            function(data) {
              // 如果有size字段，使用第三个值作为大小
              return data[2] || (formValues.pointSize || 10)
            } : 
            (formValues.pointSize || 10),
          itemStyle: {
            opacity: styleConfig.opacity || 0.8,
            color: color
          },
          emphasis: {
            itemStyle: {
              opacity: Math.min((styleConfig.opacity || 0.8) + 0.2, 1),
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.1)'
            }
          }
        })
      })
    } else {
      // 单组散点的情况
      legendData = ['Scatter']
      
      // 处理单组散点数据，支持size字段
      const scatterData = dataValues.map(item => {
        const pointData = [
          item[formValues.xField || 'x'] || 0,
          item[formValues.yField || 'y'] || 0
        ]
        
        // 如果有size字段，添加size信息
        const sizeValue = item[formValues.sizeField || 'size']
        if (sizeValue !== undefined && sizeValue !== null) {
          pointData.push(sizeValue)
        }
        
        return pointData
      })
      
      // 检查是否有size字段
      const hasSizeField = scatterData.some(point => point.length > 2)
      
      series = [{
        name: 'Scatter',
        type: 'scatter',
        data: scatterData,
        symbolSize: hasSizeField ? 
          function(data) {
            // 如果有size字段，使用第三个值作为大小
            return data[2] || (formValues.pointSize || 10)
          } : 
          (formValues.pointSize || 10),
        itemStyle: {
          opacity: styleConfig.opacity || 0.8,
          color: colors[0]
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
        trigger: 'item',
        formatter: function(params) {
          let tooltipText = `${params.seriesName}<br/>X: ${params.data[0]}<br/>Y: ${params.data[1]}`
          if (params.data.length > 2) {
            tooltipText += `<br/>Size: ${params.data[2]}`
          }
          return tooltipText
        },
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#d9d9d9',
        textStyle: {
          color: '#262626'
        }
      },
      legend: {
        data: legendData,
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
      series: series
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

export default EChartsScatterChart 