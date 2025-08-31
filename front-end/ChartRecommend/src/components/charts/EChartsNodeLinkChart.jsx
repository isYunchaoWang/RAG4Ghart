import React from 'react'
import EChartsBase from './EChartsBase'

function EChartsNodeLinkChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
  // 简单的数据适配
  let nodes = []
  let links = []
  
  try {
    if (Array.isArray(dataValues) && dataValues.length > 0) {
      console.log('开始处理关系图数据，数据条数:', dataValues.length)
      
      // 简单的数据提取
      dataValues.forEach((item, index) => {
        // 处理节点数据
        if (item.node) {
          nodes.push({
            name: item.node,
            x: item[formValues.position_xField || 'x'] || Math.random() * 100,
            y: item[formValues.position_yField || 'y'] || Math.random() * 100,
            symbolSize: item[formValues.sizeField || 'size'] || 30,
            category: item[formValues.groupField || 'group'] || 0
          })
        }
        
        // 处理连接数据
        if (item[formValues.sourceField || 'source'] && item[formValues.targetField || 'target']) {
          links.push({
            source: item[formValues.sourceField || 'source'],
            target: item[formValues.targetField || 'target'],
            value: item[formValues.valueField || 'value'] || 1
          })
        }
      })
      
      console.log('处理后的节点数:', nodes.length)
      console.log('处理后的连接数:', links.length)
    }
  } catch (error) {
    console.error('关系图数据处理错误:', error)
  }

  // 使用处理后的数据
  const simpleOption = {
    title: {
      text: title || '关系图',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        if (params.dataType === 'node') {
          const category = params.data.category || 0
          const groupName = category === 0 ? '默认组' : `组${category}`
          return `${params.data.name}<br/>位置: (${params.data.x}, ${params.data.y})<br/>大小: ${params.data.symbolSize}<br/>分组: ${groupName}`
        }
        if (params.dataType === 'edge') {
          return `${params.data.source} → ${params.data.target}<br/>连接强度: ${params.data.value}`
        }
        return params.data.name || ''
      }
    },
    series: [{
      type: 'graph',
      layout: 'none',
      symbolSize: 30,
      roam: true,
      label: {
        show: true
      },
      data: nodes,
      links: links
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
      option={simpleOption}
    />
  )
}

export default EChartsNodeLinkChart 