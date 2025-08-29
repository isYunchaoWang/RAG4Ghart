import React from 'react'
import { VegaEmbed } from 'react-vega'

export function buildBoxChartSpec({ title, description, width, height, formValues, dataValues }) {
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

  // 箱线图编码 - 需要分类轴和连续轴
  // 检查是否有group字段，如果没有则使用x字段作为分组
  const groupField = getField('group') || getField('x')
  const valueField = getField('value') || getField('y')
  
  console.log('BoxChart Debug:', {
    formValues,
    groupField,
    valueField,
    dataValues: dataValues?.slice(0, 3) // 只显示前3条数据
  })
  
  if (groupField) {
    spec.encoding.x = { 
      field: groupField, 
      type: getType('group') || getType('x') || 'nominal',
      title: '分组'
    }
  }
  if (valueField) {
    spec.encoding.y = { 
      field: valueField, 
      type: getType('value') || getType('y') || 'quantitative',
      title: '数值'
    }
  }
  if (getField('color')) {
    spec.encoding.color = { 
      field: getField('color'), 
      type: getType('color') || 'nominal' 
    }
  }

  // 构建mark配置
  const markConfig = { type: 'boxplot' }
  
  // 透明度配置
  if (formValues.opacity !== undefined && formValues.opacity !== 1) {
    markConfig.opacity = formValues.opacity
  }
  
  // 边框配置
  if (formValues.strokeWidth !== undefined && formValues.strokeWidth > 0) {
    markConfig.strokeWidth = formValues.strokeWidth
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

  // 添加字体配置 - 箱线图特定的字体配置
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



  console.log('BoxChart Spec:', spec)
  return spec
}

function BoxChart({ title, description, width, height, formValues, dataValues, onEmbed }) {
  const spec = buildBoxChartSpec({ title, description, width, height, formValues, dataValues })
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

export default BoxChart
