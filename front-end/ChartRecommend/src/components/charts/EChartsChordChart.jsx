import React from 'react'
import EChartsBase from './EChartsBase'

function EChartsChordChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
  // 数据适配
  let nodes = []
  let links = []
  const nodeMap = new Map()
  
  try {
    if (Array.isArray(dataValues) && dataValues.length > 0) {
      console.log('开始处理环状关系图数据，数据条数:', dataValues.length)
      
      // 提取所有节点
      dataValues.forEach((item, index) => {
        const source = item[formValues.sourceField || 'source']
        const target = item[formValues.targetField || 'target']
        const value = item[formValues.valueField || 'value']

        if (source && target) {
          if (!nodeMap.has(source)) {
            const nodeIndex = nodes.length
            nodeMap.set(source, nodeIndex)
            nodes.push({
              name: source,
              symbolSize: 30
            })
          }
          
          if (!nodeMap.has(target)) {
            const nodeIndex = nodes.length
            nodeMap.set(target, nodeIndex)
            nodes.push({
              name: target,
              symbolSize: 30
            })
          }
          
          links.push({
            source: nodeMap.get(source),
            target: nodeMap.get(target),
            value: value || 1
          })
        }
      })
      
      console.log('处理后的节点数:', nodes.length)
      console.log('处理后的连接数:', links.length)
    }
  } catch (error) {
    console.error('环状关系图数据处理错误:', error)
  }

  // 使用环形布局的关系图配置
  const option = {
    // title: {
    //   text: title || '环状关系图',
    //   left: 'center'
    // },
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        if (params.dataType === 'node') {
          return `${params.data.name}<br/>Node`
        }
        if (params.dataType === 'edge') {
          const sourceName = nodes[params.data.source]?.name || params.data.source
          const targetName = nodes[params.data.target]?.name || params.data.target
          return `${sourceName} → ${targetName}<br/>Connection Strength: ${params.data.value}`
        }
        return params.data.name || ''
      }
    },
    series: [{
      name: 'Chord Chart',
      type: 'graph',
      layout: 'circular',
      center: ['50%', '50%'],
      radius: '70%',
      symbolSize: 30,
      roam: true,
      label: {
        show: true,
        position: 'outside'
      },
      edgeSymbol: ['circle', 'arrow'],
      edgeSymbolSize: [4, 10],
      edgeLabel: {
        show: false
      },
      lineStyle: {
        opacity: 0.8,
        width: 1,
        curveness: 0.3
      },
      itemStyle: {
        opacity: 0.8,
        color: '#5470c6'
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 2
        },
        itemStyle: {
          opacity: 1
        }
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
      option={option}
    />
  )
}

export default EChartsChordChart 