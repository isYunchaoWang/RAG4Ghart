import React, { useMemo } from 'react'
import EChartsBase from './EChartsBase'
import { adaptDataForECharts, adaptStyleConfig } from './EChartsDataAdapter'

function EChartsNodeLinkChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
  const option = useMemo(() => {
    // 检查数据是否为空
    if (!Array.isArray(dataValues) || dataValues.length === 0) {
      return {
        title: {
          text: title || '',
          left: 'center'
        },
        series: [{
          type: 'graph',
          data: [],
          links: []
        }]
      }
    }

    const adaptedData = adaptDataForECharts('node_link', dataValues, formValues)
    const styleConfig = adaptStyleConfig('node_link', formValues)

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
          if (params.dataType === 'node') {
            const category = params.data.category || 0
            const groupName = category === 0 ? '默认组' : `组${category}`
            return `${params.data.name}<br/>位置: (${params.data.x}, ${params.data.y})<br/>大小: ${params.data.symbolSize}<br/>分组: ${groupName}`
          }
          if (params.dataType === 'edge') {
            const sourceName = adaptedData.nodes[params.data.source]?.name || params.data.source
            const targetName = adaptedData.nodes[params.data.target]?.name || params.data.target
            return `${sourceName} → ${targetName}<br/>连接强度: ${params.data.value}`
          }
          return params.data.name || ''
        }
      },
      legend: {
        data: (() => {
          const groups = new Set()
          adaptedData.nodes.forEach(node => {
            if (node.category !== undefined) {
              groups.add(node.category)
            }
          })
          const groupArray = Array.from(groups).sort()
          return groupArray.length > 0 ? groupArray.map((group, index) => `组${group}`) : ['默认组']
        })(),
        orient: formValues.legendOrientation || 'vertical',
        left: formValues.legendPosition === 'left' ? 'left' : 'right',
        textStyle: {
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
        }
      },
      series: [{
        name: '节点链接图',
        type: 'graph',
        layout: 'none',
        coordinateSystem: 'none',
        symbolSize: function(value, params) {
          return params.data.symbolSize || styleConfig.symbolSize
        },
        roam: true,
        label: {
          show: true,
          position: 'inside',
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial'
        },
        edgeSymbol: ['circle', 'arrow'],
        edgeSymbolSize: [4, 10],
        edgeLabel: {
          show: false,
          fontSize: (styleConfig.fontSize || 12) - 2,
          fontFamily: styleConfig.fontFamily || 'Arial'
        },
        lineStyle: {
          opacity: styleConfig.opacity || 0.8,
          width: styleConfig.strokeWidth || 1
        },
        itemStyle: {
          opacity: styleConfig.opacity || 0.8,
          color: function(params) {
            const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
            const category = params.data.category || 0
            const colorIndex = category % colors.length
            return colors[colorIndex] || colors[0]
          }
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: (styleConfig.strokeWidth || 1) * 2
          }
        },
        data: adaptedData.nodes,
        links: adaptedData.links,
        categories: (() => {
          const groups = new Set()
          adaptedData.nodes.forEach(node => {
            if (node.category !== undefined) {
              groups.add(node.category)
            }
          })
          const groupArray = Array.from(groups).sort()
          const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
          return groupArray.length > 0 ? groupArray.map((group, index) => ({ name: `组${group}`, itemStyle: { color: colors[index % colors.length] } })) : [{ name: '默认组', itemStyle: { color: colors[0] } }]
        })()
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

export default EChartsNodeLinkChart 