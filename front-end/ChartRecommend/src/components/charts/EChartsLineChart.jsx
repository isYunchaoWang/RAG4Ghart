import React, { useMemo } from 'react'
import EChartsBase from './EChartsBase'
import { adaptStyleConfig, getDefaultColors } from './EChartsDataAdapter'

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
    const colors = getDefaultColors('line')

    // 检查是否有color字段来分组数据
    let colorField = formValues.colorField
    
    // 自动检测：如果colorField为空或占位符，但数据中有category字段，则自动使用category
    if ((!colorField || colorField.includes('e.g.:')) && dataValues.length > 0) {
      const firstItem = dataValues[0]
      if (firstItem && firstItem.category) {
        colorField = 'category'
        console.log('Auto-detected category field for multi-line chart')
      }
    }
    
    let series = []
    let legendData = []

    // 调试信息
    console.log('Line Chart Debug:', {
      originalColorField: formValues.colorField,
      finalColorField: colorField,
      formValues,
      dataValues: dataValues.slice(0, 3) // 只显示前3条数据
    })

    // 检查是否有color字段来分组数据，并且不是占位符文本
    if (colorField && colorField.trim() && !colorField.includes('e.g.:')) {
      // 有多条线的情况 - 按color字段分组
      const groupedData = {}
      const allXValues = new Set()
      
      dataValues.forEach(item => {
        const colorValue = item[colorField] || 'Unknown'
        const xValue = item[formValues.xField || 'x'] || ''
        const yValue = item[formValues.yField || 'y'] || 0
        
        allXValues.add(xValue)
        
        if (!groupedData[colorValue]) {
          groupedData[colorValue] = {}
        }
        groupedData[colorValue][xValue] = yValue
      })

      // 获取所有X轴值并排序
      const sortedXValues = Array.from(allXValues).sort()

      // 创建多条线
      Object.keys(groupedData).forEach((colorValue, index) => {
        const color = colors[index % colors.length]
        legendData.push(colorValue)
        
        // 为每个X轴值创建数据点，如果某个X值没有数据则设为null
        const lineData = sortedXValues.map(xValue => {
          return groupedData[colorValue][xValue] !== undefined ? groupedData[colorValue][xValue] : null
        })
        
        series.push({
          name: colorValue,
          type: 'line',
          data: lineData,
          connectNulls: false, // 不连接空值点
          lineStyle: {
            width: formValues.lineWidth || 3,
            opacity: styleConfig.opacity || 0.8,
            color: color
          },
          itemStyle: {
            opacity: styleConfig.opacity || 0.8,
            color: color,
            borderColor: '#fff',
            borderWidth: 2
          },
          symbol: 'circle',
          symbolSize: formValues.pointSize || 8,
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
      // 单条线的情况
      legendData = ['Value']
      series = [{
        name: 'Value',
        type: 'line',
        data: dataValues.map(item => item[formValues.yField || 'y'] || 0),
        lineStyle: {
          width: formValues.lineWidth || 3,
          opacity: styleConfig.opacity || 0.8,
          color: colors[0]
        },
        itemStyle: {
          opacity: styleConfig.opacity || 0.8,
          color: colors[0],
          borderColor: '#fff',
          borderWidth: 2
        },
        symbol: 'circle',
        symbolSize: formValues.pointSize || 8,
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
        trigger: 'axis',
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
        type: 'category',
        data: colorField && colorField.trim() && !colorField.includes('e.g.:') 
          ? Array.from(new Set(dataValues.map(item => item[formValues.xField || 'x'] || ''))).sort()
          : dataValues.map(item => item[formValues.xField || 'x'] || ''),
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

export default EChartsLineChart 