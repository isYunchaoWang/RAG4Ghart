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
      try {
        console.log('EChartsBase 开始初始化图表，类型:', chartType)
        
        // 初始化图表
        const chart = echarts.init(chartRef.current)
        chartInstance.current = chart
        
        console.log('ECharts 实例创建成功')
        
        // 设置图表配置
        if (option) {
          console.log('设置 ECharts 配置:', option)
          chart.setOption(option)
          console.log('ECharts 配置设置成功')
        }
        
        // 回调函数
        if (onEmbed && chart) {
          onEmbed({ view: chart })
          console.log('ECharts 回调函数执行成功')
        }
      } catch (error) {
        console.error('ECharts初始化错误:', error)
        console.error('图表类型:', chartType)
        console.error('配置:', option)
        
        // 显示错误信息在页面上
        if (chartRef.current) {
          chartRef.current.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #ff4d4f; font-size: 14px;">
              图表渲染失败: ${error.message}
            </div>
          `
        }
      }
    }

    return () => {
      if (chartInstance.current) {
        console.log('EChartsBase 清理图表实例')
        chartInstance.current.dispose()
      }
    }
  }, [])

  useEffect(() => {
    if (chartInstance.current && option) {
      try {
        console.log('EChartsBase 更新图表配置:', option)
        chartInstance.current.setOption(option, true)
        console.log('EChartsBase 图表配置更新成功')
      } catch (error) {
        console.error('ECharts渲染错误:', error)
        console.error('问题配置:', option)
        
        // 显示错误信息
        if (chartRef.current) {
          chartRef.current.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #ff4d4f; font-size: 14px;">
              图表更新失败: ${error.message}
            </div>
          `
        }
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