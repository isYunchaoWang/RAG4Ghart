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

  // Extract fields and types from form values
  const getField = (fieldName) => formValues[`${fieldName}Field`]
  const getType = (fieldName) => formValues[`${fieldName}Type`]

  // Pie chart uses theta encoding
  if (getField('value')) spec.encoding.theta = { field: getField('value'), type: getType('value') || 'quantitative' }
  if (getField('category')) spec.encoding.color = { field: getField('category'), type: getType('category') || 'nominal' }

  // Build mark configuration
  const markConfig = { type: 'arc' }
  
  // Opacity configuration
  if (formValues.opacity !== undefined && formValues.opacity !== 1) {
    markConfig.opacity = formValues.opacity
  }
  
  // Border configuration
  if (formValues.strokeWidth !== undefined && formValues.strokeWidth > 0) {
    markConfig.stroke = formValues.strokeColor || '#000'
    markConfig.strokeWidth = formValues.strokeWidth
  }
  
  // Pie chart inner radius configuration
  if (formValues.innerRadius !== undefined && formValues.innerRadius > 0) {
    markConfig.innerRadius = formValues.innerRadius
  }

  // Color configuration
  if (spec.encoding.color) {
    // If there is a color scheme, use the color scheme
    if (formValues.colorScheme) {
      spec.encoding.color = {
        ...spec.encoding.color,
        scale: { scheme: formValues.colorScheme }
      }
    }
    // If there is a primary color and no color scheme, use the primary color
    else if (formValues.markColor) {
      spec.encoding.color = {
        ...spec.encoding.color,
        scale: { range: [formValues.markColor] }
      }
    }
  }

  spec.mark = markConfig

  // Add legend configuration
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

  // Add font configuration - pie chart specific font configuration
  if (formValues.fontFamily || formValues.fontSize || formValues.fontColor) {
    spec.config = spec.config || {}
    spec.config.title = spec.config.title || {}
    spec.config.legend = spec.config.legend || {}
    
    // Title font configuration
    if (formValues.fontFamily) spec.config.title.font = formValues.fontFamily
    if (formValues.fontSize) spec.config.title.fontSize = formValues.fontSize
    if (formValues.fontColor) spec.config.title.color = formValues.fontColor
    
    // Legend label font configuration
    if (formValues.fontFamily) spec.config.legend.labelFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.legend.labelFontSize = formValues.fontSize
    if (formValues.fontColor) spec.config.legend.labelColor = formValues.fontColor
    
    // Legend title font configuration
    if (formValues.fontFamily) spec.config.legend.titleFont = formValues.fontFamily
    if (formValues.fontSize) spec.config.legend.titleFontSize = formValues.fontSize
    if (formValues.fontColor) spec.config.legend.titleColor = formValues.fontColor
  }

  // Add interaction configuration
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
