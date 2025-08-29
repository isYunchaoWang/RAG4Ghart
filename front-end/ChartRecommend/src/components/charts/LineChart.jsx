import React from 'react'
import { VegaEmbed } from 'react-vega'

export function buildLineChartSpec({ title, description, width, height, formValues, dataValues }) {
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

  // 基础编码
  if (getField('x')) spec.encoding.x = { field: getField('x'), type: getType('x') || 'ordinal' }
  if (getField('y')) spec.encoding.y = { field: getField('y'), type: getType('y') || 'quantitative' }
  if (getField('color')) spec.encoding.color = { field: getField('color'), type: getType('color') || 'nominal' }



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

  spec.mark = markConfig

  // 添加轴配置
  if (formValues.showGrid !== undefined) {
    spec.config = spec.config || {}
    spec.config.axis = spec.config.axis || {}
    
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
  if (formValues.fontFamily || formValues.fontSize) {
    spec.config = spec.config || {}
    spec.config.title = spec.config.title || {}
    spec.config.axis = spec.config.axis || {}
    spec.config.legend = spec.config.legend || {}
    
    // 标题字体配置
    if (formValues.fontFamily) spec.config.title.font = formValues.fontFamily
    if (formValues.fontSize) spec.config.title.fontSize = formValues.fontSize
    
    // 轴标签字体配置
    if (formValues.fontFamily) spec.config.axis.labelFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.axis.labelFontSize = formValues.fontSize
    
    // 轴标题字体配置
    if (formValues.fontFamily) spec.config.axis.titleFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.axis.titleFontSize = formValues.fontSize
    
    // 图例标签字体配置
    if (formValues.fontFamily) spec.config.legend.labelFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.legend.labelFontSize = formValues.fontSize
    
    // 图例标题字体配置
    if (formValues.fontFamily) spec.config.legend.titleFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.legend.titleFontSize = formValues.fontSize
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
