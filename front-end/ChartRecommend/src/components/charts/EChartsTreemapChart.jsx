import React from 'react'
import EChartsBase from './EChartsBase'

function EChartsTreemapChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
  // 数据适配
  let treemapData = []
  
  try {
    if (Array.isArray(dataValues) && dataValues.length > 0) {
      console.log('开始处理矩形树图数据，数据条数:', dataValues.length)
      
      // 处理数据
      dataValues.forEach((item, index) => {
        const category = item[formValues.categoryField || 'category']
        const size = item[formValues.sizeField || 'size']
        const color = item[formValues.colorField || 'color']
        
        if (category && size) {
          treemapData.push({
            name: category,
            value: size,
            itemStyle: {
              color: color ? `#${Math.floor(Math.random()*16777215).toString(16)}` : undefined
            }
          })
        }
      })
      
      console.log('处理后的矩形树图数据:', treemapData)
    }
  } catch (error) {
    console.error('矩形树图数据处理错误:', error)
  }

  // 矩形树图配置
  const option = {
    title: {
      text: title || 'Treemap',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        return `${params.data.name}<br/>Size: ${params.data.value}`
      }
    },
    series: [{
      name: 'Treemap',
      type: 'treemap',
      data: treemapData,
      label: {
        show: true,
        formatter: '{b}'
      },
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 1,
        gapWidth: 2
      },
      emphasis: {
        itemStyle: {
          borderColor: '#333',
          borderWidth: 2
        }
      }
    }]
  }

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

export default EChartsTreemapChart 