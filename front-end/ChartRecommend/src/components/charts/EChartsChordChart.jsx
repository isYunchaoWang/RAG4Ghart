import React, { useMemo } from 'react'
import EChartsBase from './EChartsBase'
import { adaptDataForECharts, adaptStyleConfig } from './EChartsDataAdapter'

function EChartsChordChart({ chartType, title, description, width, height, formValues, dataValues, onEmbed }) {
  const option = useMemo(() => {
    // 检查数据是否为空
    if (!Array.isArray(dataValues) || dataValues.length === 0) {
      return {
        title: {
          text: title || '',
          left: 'center'
        },
        series: [{
          type: 'chord',
          data: [],
          links: []
        }]
      }
    }

    const adaptedData = adaptDataForECharts('chord', dataValues, formValues)
    const styleConfig = adaptStyleConfig('chord', formValues)

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
          if (params.dataType === 'edge') {
            const sourceName = adaptedData.nodes[params.data.source]?.name || params.data.source
            const targetName = adaptedData.nodes[params.data.target]?.name || params.data.target
            return `${sourceName} → ${targetName}<br/>连接强度: ${params.data.value}`
          }
          if (params.dataType === 'node') {
            return `${params.data.name}<br/>节点`
          }
          return params.data.name || ''
        }
      },
      series: [{
        type: 'chord',
        center: ['50%', '50%'],
        radius: '70%',
        data: adaptedData.nodes,
        links: adaptedData.links,
        categories: adaptedData.nodes.length > 0 ? adaptedData.nodes.map((node, index) => ({ 
          name: node.name
        })) : [],
        label: {
          show: true,
          position: 'outside',
          fontSize: styleConfig.fontSize || 12,
          fontFamily: styleConfig.fontFamily || 'Arial',
          color: '#333'
        },
        itemStyle: {
          opacity: styleConfig.opacity || 0.8,
          borderWidth: styleConfig.strokeWidth || 1,
          borderColor: '#fff'
        },
        lineStyle: {
          opacity: styleConfig.opacity || 0.8,
          width: styleConfig.strokeWidth || 1
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: (styleConfig.strokeWidth || 1) * 2
          },
          itemStyle: {
            opacity: 1
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

export default EChartsChordChart 