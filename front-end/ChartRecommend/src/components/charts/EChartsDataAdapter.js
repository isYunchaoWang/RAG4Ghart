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
    links: links
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
  console.log('adaptNodeLinkData 开始执行，输入:', { 
    dataValues: dataValues?.length, 
    formValues: Object.keys(formValues || {}) 
  })
  
  if (!Array.isArray(dataValues) || dataValues.length === 0) {
    console.log('adaptNodeLinkData 数据为空')
    return { nodes: [], links: [] }
  }

  const nodes = []
  const links = []
  const nodeMap = new Map()

  console.log('开始处理节点数据...')
  // 首先处理节点数据
  dataValues.forEach((item, index) => {
    const nodeName = item[formValues.nodeField || 'node']
    const x = item[formValues.xField || 'x']
    const y = item[formValues.yField || 'y']
    const group = item[formValues.groupField || 'group']
    const size = item[formValues.sizeField || 'size']

    if (nodeName) {
      const nodeIndex = nodes.length
      nodeMap.set(nodeName, nodeIndex)
      
      const node = {
        name: nodeName,
        x: x || 0,
        y: y || 0,
        category: group || 0,
        symbolSize: size || 30
      }
      
      nodes.push(node)
      console.log(`添加节点 ${index}:`, node)
    }
  })

  console.log('开始处理连接数据...')
  // 然后处理连接数据
  dataValues.forEach((item, index) => {
    const source = item[formValues.sourceField || 'source']
    const target = item[formValues.targetField || 'target']
    const value = item[formValues.valueField || 'value']

    if (source && target) {
      // 如果节点不存在，创建默认节点
      if (!nodeMap.has(source)) {
        const nodeIndex = nodes.length
        nodeMap.set(source, nodeIndex)
        const defaultNode = {
          name: source,
          x: Math.random() * 100,
          y: Math.random() * 100,
          category: 0,
          symbolSize: 30
        }
        nodes.push(defaultNode)
        console.log(`创建默认源节点:`, defaultNode)
      }
      
      if (!nodeMap.has(target)) {
        const nodeIndex = nodes.length
        nodeMap.set(target, nodeIndex)
        const defaultNode = {
          name: target,
          x: Math.random() * 100,
          y: Math.random() * 100,
          category: 0,
          symbolSize: 30
        }
        nodes.push(defaultNode)
        console.log(`创建默认目标节点:`, defaultNode)
      }

      const link = {
        source: nodeMap.get(source),
        target: nodeMap.get(target),
        value: value || 1
      }
      links.push(link)
      console.log(`添加连接 ${index}:`, link)
    }
  })

  // 如果没有连接数据，但有点数据，创建一些示例连接
  if (links.length === 0 && nodes.length > 1) {
    console.log('没有连接数据，创建示例连接...')
    for (let i = 0; i < nodes.length - 1; i++) {
      const link = {
        source: i,
        target: i + 1,
        value: 1
      }
      links.push(link)
      console.log(`创建示例连接 ${i}:`, link)
    }
    // 添加一个环形连接
    if (nodes.length > 2) {
      const ringLink = {
        source: nodes.length - 1,
        target: 0,
        value: 1
      }
      links.push(ringLink)
      console.log('创建环形连接:', ringLink)
    }
  }

  const result = { nodes, links }
  console.log('adaptNodeLinkData 完成，结果:', result)
  return result
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