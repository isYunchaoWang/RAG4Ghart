import React, { useEffect, useRef } from 'react'
import * as echarts from 'echarts'

function EChartsBase({ 
  chartType, 
  title, 
  description, 
  width, 
  height, 
  formValues, 
  dataValues, 
  onEmbed,
  option 
}) {
  const chartRef = useRef(null)
  const chartInstance = useRef(null)

  useEffect(() => {
    if (chartRef.current) {
      // 初始化图表
      chartInstance.current = echarts.init(chartRef.current)
      
      // 设置图表配置
      if (option) {
        chartInstance.current.setOption(option)
      }
      
      // 回调函数
      if (onEmbed && chartInstance.current) {
        onEmbed({ view: chartInstance.current })
      }
    }

    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose()
      }
    }
  }, [])

  useEffect(() => {
    if (chartInstance.current && option) {
      try {
        chartInstance.current.setOption(option, true)
      } catch (error) {
        console.error('ECharts渲染错误:', error)
        console.error('问题配置:', option)
        // 尝试使用最小配置重新渲染
        chartInstance.current.setOption({
          title: { text: '图表渲染失败' },
          series: [{ type: 'bar', data: [] }]
        }, true)
      }
    }
  }, [option])

  useEffect(() => {
    if (chartInstance.current) {
      chartInstance.current.resize()
    }
  }, [width, height])

  return (
    <div 
      ref={chartRef} 
      style={{ 
        width: width || '100%', 
        height: height || '100%',
        minHeight: '300px'
      }} 
    />
  )
}

export default EChartsBase 