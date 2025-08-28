import React from 'react'
import { VegaEmbed } from 'react-vega'

function buildPieChartSpec({ title, description, width, height, formValues, dataValues }) {
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

  // 饼图使用 theta 编码
  if (getField('value')) spec.encoding.theta = { field: getField('value'), type: getType('value') || 'quantitative' }
  if (getField('category')) spec.encoding.color = { field: getField('category'), type: getType('category') || 'nominal' }

  // 构建mark配置
  const markConfig = { type: 'arc' }
  
  // 透明度配置
  if (formValues.opacity !== undefined && formValues.opacity !== 1) {
    markConfig.opacity = formValues.opacity
  }
  
  // 边框配置
  if (formValues.strokeWidth !== undefined && formValues.strokeWidth > 0) {
    markConfig.stroke = formValues.strokeColor || '#000'
    markConfig.strokeWidth = formValues.strokeWidth
  }
  
  // 饼图内半径配置
  if (formValues.innerRadius !== undefined && formValues.innerRadius > 0) {
    markConfig.innerRadius = formValues.innerRadius
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
  }

  spec.mark = markConfig

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

  // 添加字体配置 - 饼图特定的字体配置
  if (formValues.fontFamily || formValues.fontSize || formValues.fontColor) {
    spec.config = spec.config || {}
    spec.config.title = spec.config.title || {}
    spec.config.legend = spec.config.legend || {}
    
    // 标题字体配置
    if (formValues.fontFamily) spec.config.title.font = formValues.fontFamily
    if (formValues.fontSize) spec.config.title.fontSize = formValues.fontSize
    if (formValues.fontColor) spec.config.title.color = formValues.fontColor
    
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

function PieChart({ title, description, width, height, formValues, dataValues, onEmbed }) {
  const spec = buildPieChartSpec({ title, description, width, height, formValues, dataValues })
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

export default PieChart
