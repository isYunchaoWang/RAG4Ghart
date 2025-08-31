// 数据适配器 - 将表单数据转换为ECharts格式
export function adaptDataForECharts(chartType, dataValues, formValues) {
  switch (chartType) {
    case 'chord':
      return adaptChordData(dataValues, formValues)
    case 'funnel':
      return adaptFunnelData(dataValues, formValues)
    case 'node_link':
      return adaptNodeLinkData(dataValues, formValues)
    case 'sankey':
      return adaptSankeyData(dataValues, formValues)
    default:
      return dataValues
  }
}

// 弦图数据适配
function adaptChordData(dataValues, formValues) {
  if (!Array.isArray(dataValues) || dataValues.length === 0) {
    return { nodes: [], links: [] }
  }

  const nodes = new Set()
  const links = []

  dataValues.forEach(item => {
    const source = item[formValues.sourceField || 'source']
    const target = item[formValues.targetField || 'target']
    const value = item[formValues.valueField || 'value']

    if (source && target) {
      nodes.add(source)
      nodes.add(target)
      links.push({
        source,
        target,
        value: value || 1
      })
    }
  })

  return {
    nodes: Array.from(nodes).map(name => ({ name })),
    links
  }
}

// 漏斗图数据适配
function adaptFunnelData(dataValues, formValues) {
  if (!Array.isArray(dataValues) || dataValues.length === 0) {
    return []
  }

  return dataValues.map(item => ({
    value: item[formValues.valueField || 'value'] || 0,
    name: item[formValues.stageField || 'stage'] || '',
    rate: item[formValues.rateField || 'rate'] || 0
  }))
}

// 节点链接图数据适配
function adaptNodeLinkData(dataValues, formValues) {
  if (!Array.isArray(dataValues) || dataValues.length === 0) {
    return { nodes: [], links: [] }
  }

  const nodes = []
  const links = []
  const nodeMap = new Map()

  // 首先处理节点数据
  dataValues.forEach(item => {
    const nodeName = item[formValues.nodeField || 'node']
    const x = item[formValues.xField || 'x']
    const y = item[formValues.yField || 'y']
    const group = item[formValues.groupField || 'group']
    const size = item[formValues.sizeField || 'size']

    if (nodeName) {
      const nodeIndex = nodes.length
      nodeMap.set(nodeName, nodeIndex)
      
      nodes.push({
        name: nodeName,
        x: x || 0,
        y: y || 0,
        category: group || 0,
        symbolSize: size || 30
      })
    }
  })

  // 然后处理连接数据（如果有的话）
  // 如果数据中包含source和target字段，则创建连接
  dataValues.forEach(item => {
    const source = item[formValues.sourceField || 'source']
    const target = item[formValues.targetField || 'target']
    const value = item[formValues.valueField || 'value']

    if (source && target && nodeMap.has(source) && nodeMap.has(target)) {
      links.push({
        source: nodeMap.get(source),
        target: nodeMap.get(target),
        value: value || 1
      })
    }
  })

  // 如果没有明确的连接数据，则根据节点位置创建一些示例连接
  if (links.length === 0 && nodes.length > 1) {
    for (let i = 0; i < nodes.length - 1; i++) {
      links.push({
        source: i,
        target: i + 1,
        value: 1
      })
    }
  }

  return { nodes, links }
}

// 桑基图数据适配
function adaptSankeyData(dataValues, formValues) {
  if (!Array.isArray(dataValues) || dataValues.length === 0) {
    return { nodes: [], links: [] }
  }

  const nodes = new Set()
  const links = []

  dataValues.forEach(item => {
    const source = item[formValues.sourceField || 'source']
    const target = item[formValues.targetField || 'target']
    const value = item[formValues.valueField || 'value']

    if (source && target) {
      nodes.add(source)
      nodes.add(target)
      links.push({
        source,
        target,
        value: value || 1
      })
    }
  })

  return {
    nodes: Array.from(nodes).map(name => ({ name })),
    links
  }
}

// 样式配置适配器
export function adaptStyleConfig(chartType, formValues) {
  // 确保formValues是对象
  const safeFormValues = formValues || {}
  
  const baseConfig = {
    opacity: safeFormValues.opacity !== undefined ? safeFormValues.opacity : 0.8,
    fontSize: safeFormValues.fontSize || 12,
    fontFamily: safeFormValues.fontFamily || 'Arial'
  }

  switch (chartType) {
    case 'bar':
      return {
        ...baseConfig,
        cornerRadius: safeFormValues.cornerRadius || 0
      }
    case 'line':
      return {
        ...baseConfig,
        lineWidth: safeFormValues.lineWidth || 2,
        pointSize: safeFormValues.pointSize || 6
      }
    case 'pie':
      return {
        ...baseConfig,
        innerRadius: safeFormValues.innerRadius || 0
      }
    case 'scatter':
    case 'bubble':
      return {
        ...baseConfig,
        pointSize: safeFormValues.pointSize || 10
      }
    case 'heatmap':
    case 'treemap':
      return baseConfig
    case 'chord':
      return {
        ...baseConfig,
        innerRadius: safeFormValues.innerRadius || 60,
        strokeWidth: safeFormValues.strokeWidth || 1
      }
    case 'funnel':
      return {
        ...baseConfig,
        gap: safeFormValues.gap || 2,
        sort: safeFormValues.sort || 'descending'
      }
    case 'node_link':
      return {
        ...baseConfig,
        symbolSize: safeFormValues.pointSize || 30,
        strokeWidth: safeFormValues.strokeWidth || 1
      }
    default:
      return baseConfig
  }
} 