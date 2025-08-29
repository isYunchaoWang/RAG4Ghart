import React from 'react'
import { VegaEmbed } from 'react-vega'

export function buildPieChartSpec({ title, description, width, height, formValues, dataValues }) {
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
    markConfig.strokeWidth = formValues.strokeWidth
  }
  
  // 饼图内半径配置
  if (formValues.innerRadius !== undefined && formValues.innerRadius > 0) {
    markConfig.innerRadius = formValues.innerRadius
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
  if (formValues.fontFamily || formValues.fontSize) {
    spec.config = spec.config || {}
    spec.config.title = spec.config.title || {}
    spec.config.legend = spec.config.legend || {}
    
    // 标题字体配置
    if (formValues.fontFamily) spec.config.title.font = formValues.fontFamily
    if (formValues.fontSize) spec.config.title.fontSize = formValues.fontSize
    
    // 图例标签字体配置
    if (formValues.fontFamily) spec.config.legend.labelFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.legend.labelFontSize = formValues.fontSize
    
    // 图例标题字体配置
    if (formValues.fontFamily) spec.config.legend.titleFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.legend.titleFontSize = formValues.fontSize
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
