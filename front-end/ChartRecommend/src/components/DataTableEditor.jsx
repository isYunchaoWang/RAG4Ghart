import React, { useState, useEffect } from 'react'
import { Input, Button, Space, message, Alert, Typography, Card, Tooltip } from 'antd'
import { UploadOutlined, DownloadOutlined, CopyOutlined, ReloadOutlined } from '@ant-design/icons'

const { TextArea } = Input
const { Text } = Typography

function DataTableEditor({ value, onChange, chartType }) {
  const [jsonText, setJsonText] = useState('')
  const [isValid, setIsValid] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')

  // 根据图表类型生成默认数据
  const getDefaultData = (type) => {
    switch (type) {
      case 'bar':
        return [
          { x: 'A', y: 10 },
          { x: 'B', y: 20 },
          { x: 'C', y: 15 },
          { x: 'D', y: 25 }
        ]
      case 'line':
        return [
          { x: '2023-01', y: 10 },
          { x: '2023-02', y: 20 },
          { x: '2023-03', y: 15 },
          { x: '2023-04', y: 25 }
        ]
      case 'scatter':
      case 'bubble':
        return [
          { x: 10, y: 15, size: 20, category: 'A类' },
          { x: 20, y: 25, size: 35, category: 'A类' },
          { x: 30, y: 35, size: 50, category: 'B类' },
          { x: 40, y: 45, size: 65, category: 'B类' }
        ]
      case 'pie':
        return [
          { category: '分类A', value: 30 },
          { category: '分类B', value: 25 },
          { category: '分类C', value: 20 },
          { category: '分类D', value: 15 },
          { category: '分类E', value: 10 }
        ]
      case 'heatmap':
        return [
          { x: 'A', y: 'X', value: 10 },
          { x: 'A', y: 'Y', value: 20 },
          { x: 'B', y: 'X', value: 15 },
          { x: 'B', y: 'Y', value: 25 },
          { x: 'C', y: 'X', value: 30 },
          { x: 'C', y: 'Y', value: 35 }
        ]
      case 'treemap':
        return [
          { category: 'A', size: 100 }, { category: 'B', size: 200 }, 
          { category: 'C', size: 150 }, { category: 'D', size: 80 }
        ]
      default:
        return [
          { x: 1, y: 10 },
          { x: 2, y: 20 },
          { x: 3, y: 15 },
          { x: 4, y: 25 }
        ]
    }
  }

  // 获取数据格式说明
  const getDataFormatDescription = (type) => {
    switch (type) {
      case 'bar':
        return '格式：数组对象，每个对象包含 x（类别）和 y（数值）字段'
      case 'line':
        return '格式：数组对象，每个对象包含 x（时间/类别）和 y（数值）字段'
      case 'scatter':
      case 'bubble':
        return '格式：数组对象，每个对象包含 x（X轴）、y（Y轴）、size（大小，可选）、category（分类，可选）字段'
      case 'pie':
        return '格式：数组对象，每个对象包含 category（分类）和 value（数值）字段'
      case 'heatmap':
        return '格式：数组对象，每个对象包含 x（X轴）、y（Y轴）和 value（数值）字段'
      case 'treemap':
        return '格式：数组对象，每个对象包含 category（分类）和 size（大小）字段'
      default:
        return '格式：数组对象，每个对象包含 x（X轴）和 y（Y轴）字段'
    }
  }

  // 验证JSON格式
  const validateJSON = (text) => {
    try {
      if (!text.trim()) {
        setIsValid(true)
        setErrorMessage('')
        return null
      }
      const parsed = JSON.parse(text)
      if (!Array.isArray(parsed)) {
        setIsValid(false)
        setErrorMessage('数据必须是数组格式')
        return null
      }
      setIsValid(true)
      setErrorMessage('')
      return parsed
    } catch (error) {
      setIsValid(false)
      setErrorMessage(`JSON格式错误: ${error.message}`)
      return null
    }
  }

  // 处理JSON文本变化
  const handleJsonChange = (e) => {
    const text = e.target.value
    setJsonText(text)
    const parsed = validateJSON(text)
    if (parsed !== null) {
      onChange?.(parsed)
    }
  }

  // 初始化数据
  useEffect(() => {
    if (value && Array.isArray(value)) {
      setJsonText(JSON.stringify(value, null, 2))
      setIsValid(true)
      setErrorMessage('')
    } else {
      const defaultData = getDefaultData(chartType)
      setJsonText(JSON.stringify(defaultData, null, 2))
      setIsValid(true)
      setErrorMessage('')
      onChange?.(defaultData)
    }
  }, [value, chartType, onChange])

  // 重置为默认数据
  const resetToDefault = () => {
    const defaultData = getDefaultData(chartType)
    setJsonText(JSON.stringify(defaultData, null, 2))
    setIsValid(true)
    setErrorMessage('')
    onChange?.(defaultData)
    message.success('已重置为默认数据')
  }

  // 复制JSON到剪贴板
  const copyToClipboard = () => {
    navigator.clipboard.writeText(jsonText).then(() => {
      message.success('JSON已复制到剪贴板')
    }).catch(() => {
      message.error('复制失败')
    })
  }

  // 导入JSON文件
  const importJSON = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.json'
    input.onchange = (e) => {
      const file = e.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (event) => {
          try {
            const jsonText = event.target.result
            const parsed = JSON.parse(jsonText)
            if (!Array.isArray(parsed)) {
              message.error('文件内容必须是数组格式')
              return
            }
            setJsonText(JSON.stringify(parsed, null, 2))
            setIsValid(true)
            setErrorMessage('')
            onChange?.(parsed)
            message.success('JSON文件导入成功')
          } catch (error) {
            message.error('JSON文件格式错误')
          }
        }
        reader.readAsText(file)
      }
    }
    input.click()
  }

  // 导出JSON文件
  const exportJSON = () => {
    if (!jsonText.trim()) {
      message.warning('没有数据可导出')
      return
    }
    
    const blob = new Blob([jsonText], { type: 'application/json;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'chart_data.json')
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    message.success('JSON文件导出成功')
  }

  return (
    <div>
      {/* 数据格式说明 */}
      <Card size="small" style={{ marginBottom: 8 }}>
        <div style={{ fontSize: '12px', color: '#666' }}>
          <Text strong>数据格式说明：</Text>
          <br />
          {getDataFormatDescription(chartType)}
        </div>
      </Card>

      {/* 操作按钮 */}
      <Space style={{ marginBottom: 8 }}>
        <Tooltip title="重置为默认数据">
          <Button size="small" icon={<ReloadOutlined />} onClick={resetToDefault}>
            重置
          </Button>
        </Tooltip>
        <Tooltip title="复制JSON到剪贴板">
          <Button size="small" icon={<CopyOutlined />} onClick={copyToClipboard}>
            复制
          </Button>
        </Tooltip>
        <Button size="small" icon={<UploadOutlined />} onClick={importJSON}>
          导入JSON
        </Button>
        <Button size="small" icon={<DownloadOutlined />} onClick={exportJSON}>
          导出JSON
        </Button>
      </Space>

      {/* 错误提示 */}
      {!isValid && (
        <Alert
          message="JSON格式错误"
          description={errorMessage}
          type="error"
          showIcon
          style={{ marginBottom: 8 }}
        />
      )}

      {/* JSON输入框 */}
      <TextArea
        value={jsonText}
        onChange={handleJsonChange}
        placeholder="请输入JSON格式的数据..."
        rows={12}
        style={{
          fontFamily: 'Monaco, Menlo, Consolas, monospace',
          fontSize: '12px',
          borderColor: isValid ? undefined : '#ff4d4f'
        }}
      />

      {/* 数据预览 */}
      {isValid && jsonText.trim() && (
        <div style={{ marginTop: 8, fontSize: '12px', color: '#666' }}>
          <Text>数据预览：共 {JSON.parse(jsonText).length} 条记录</Text>
        </div>
      )}
    </div>
  )
}

export default DataTableEditor
