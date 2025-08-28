import React from 'react'
import { VegaEmbed } from 'react-vega'

function buildLineChartSpec({ title, description, width, height, formValues, dataValues }) {
  const spec = {
    $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
    description: description || undefined,
    title: title || undefined,
    width: width || 180,
    height: height || undefined,
    data: { values: Array.isArray(dataValues) ? dataValues : [] },
    encoding: {}
  }

  // 从表单值中提取字段和类型
  const getField = (fieldName) => formValues[`${fieldName}Field`]
  const getType = (fieldName) => formValues[`${fieldName}Type`]
  const aggregate = formValues.aggregate

  // 基础编码
  if (getField('x')) spec.encoding.x = { field: getField('x'), type: getType('x') || 'ordinal' }
  if (getField('y')) spec.encoding.y = { field: getField('y'), type: getType('y') || 'quantitative' }
  if (getField('color')) spec.encoding.color = { field: getField('color'), type: getType('color') || 'nominal' }

  // 聚合函数处理
  if (aggregate && spec.encoding.y) {
    spec.encoding.y = {
      ...spec.encoding.y,
      aggregate: aggregate,
    }
  }

  // 构建mark配置
  const markConfig = { type: 'line' }
  
  // 透明度配置
  if (formValues.opacity !== undefined && formValues.opacity !== 1) {
    markConfig.opacity = formValues.opacity
  }
  
  // 线条宽度配置
  if (formValues.lineWidth !== undefined && formValues.lineWidth > 0) {
    markConfig.strokeWidth = formValues.lineWidth
  }
  
  // 线条样式配置（虚线等）
  if (formValues.strokeDash && formValues.strokeDash.length > 0) {
    markConfig.strokeDash = formValues.strokeDash
  }

  // 颜色配置
  if (spec.encoding.color) {
    // 如果有颜色方案，使用颜色方案
    if (formValues.colorScheme) {
      spec.encoding.color = {
        ...spec.encoding.color,
        scale: { scheme: formValues.colorScheme }
      }
    }
    // 如果有主色调且没有颜色方案，使用主色调
    else if (formValues.markColor) {
      spec.encoding.color = {
        ...spec.encoding.color,
        scale: { range: [formValues.markColor] }
      }
    }
  } else {
    // 如果没有color字段但有主色调，设置mark的color
    if (formValues.markColor) {
      markConfig.stroke = formValues.markColor
    }
  }

  // 边框配置（线条的边框色）
  if (formValues.strokeColor) {
    markConfig.stroke = formValues.strokeColor
  }

  spec.mark = markConfig

  // 添加轴配置
  if (formValues.xAxisPosition || formValues.yAxisPosition || formValues.showGrid !== undefined) {
    spec.config = spec.config || {}
    spec.config.axis = spec.config.axis || {}
    
    if (formValues.xAxisPosition) {
      spec.config.axis.x = { ...spec.config.axis.x, orient: formValues.xAxisPosition }
    }
    if (formValues.yAxisPosition) {
      spec.config.axis.y = { ...spec.config.axis.y, orient: formValues.yAxisPosition }
    }
    if (formValues.showGrid === false) {
      spec.config.axis.grid = false
    }
  }

  // 添加图例配置
  if (formValues.showLegend === false || formValues.legendPosition || formValues.legendOrientation) {
    spec.config = spec.config || {}
    spec.config.legend = spec.config.legend || {}
    
    if (formValues.showLegend === false) {
      spec.config.legend.disable = true
    }
    if (formValues.legendPosition) {
      spec.config.legend.orient = formValues.legendPosition
    }
    if (formValues.legendOrientation) {
      spec.config.legend.direction = formValues.legendOrientation
    }
  }

  // 添加字体配置 - 线图特定的字体配置
  if (formValues.fontFamily || formValues.fontSize || formValues.fontColor) {
    spec.config = spec.config || {}
    spec.config.title = spec.config.title || {}
    spec.config.axis = spec.config.axis || {}
    spec.config.legend = spec.config.legend || {}
    
    // 标题字体配置
    if (formValues.fontFamily) spec.config.title.font = formValues.fontFamily
    if (formValues.fontSize) spec.config.title.fontSize = formValues.fontSize
    if (formValues.fontColor) spec.config.title.color = formValues.fontColor
    
    // 轴标签字体配置
    if (formValues.fontFamily) spec.config.axis.labelFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.axis.labelFontSize = formValues.fontSize
    if (formValues.fontColor) spec.config.axis.labelColor = formValues.fontColor
    
    // 轴标题字体配置
    if (formValues.fontFamily) spec.config.axis.titleFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.axis.titleFontSize = formValues.fontSize
    if (formValues.fontColor) spec.config.axis.titleColor = formValues.fontColor
    
    // 图例标签字体配置
    if (formValues.fontFamily) spec.config.legend.labelFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.legend.labelFontSize = formValues.fontSize
    if (formValues.fontColor) spec.config.legend.labelColor = formValues.fontColor
    
    // 图例标题字体配置
    if (formValues.fontFamily) spec.config.legend.titleFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.legend.titleFontSize = formValues.fontSize
    if (formValues.fontColor) spec.config.legend.titleColor = formValues.fontColor
  }

  // 添加交互配置
  if (formValues.enableTooltip === false || formValues.enableZoom || formValues.enablePan || formValues.enableSelection) {
    spec.config = spec.config || {}
    
    if (formValues.enableTooltip === false) {
      spec.config.tooltip = { disable: true }
    }
    
    if (formValues.enableZoom || formValues.enablePan || formValues.enableSelection) {
      spec.selection = spec.selection || {}
      
      if (formValues.enableZoom) {
        spec.selection.zoom = { type: 'interval', bind: 'scales' }
      }
      if (formValues.enablePan) {
        spec.selection.pan = { type: 'interval', bind: 'scales' }
      }
      if (formValues.enableSelection) {
        spec.selection.select = { type: 'multi', bind: 'legend' }
      }
    }
  }

  return spec
}

function LineChart({ title, description, width, height, formValues, dataValues, onEmbed }) {
  const spec = buildLineChartSpec({ title, description, width, height, formValues, dataValues })
  const embedOptions = { actions: false, mode: 'vega-lite' }

  return (
    <VegaEmbed 
      spec={spec} 
      options={embedOptions} 
      style={{ width: '100%', height: '100%' }} 
      onEmbed={onEmbed} 
    />
  )
}

export default LineChart
