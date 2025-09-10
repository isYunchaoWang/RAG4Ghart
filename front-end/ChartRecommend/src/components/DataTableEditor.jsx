import React, { useState, useEffect } from 'react'
import { Input, Button, Space, message, Alert, Typography, Card, Tooltip } from 'antd'
import { UploadOutlined, DownloadOutlined, CopyOutlined, ReloadOutlined } from '@ant-design/icons'

const { TextArea } = Input
const { Text } = Typography

function DataTableEditor({ value, onChange, chartType }) {
  const [jsonText, setJsonText] = useState('')
  const [isValid, setIsValid] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')
  const [isUserEditing, setIsUserEditing] = useState(false)

  // Generate default data based on chart type
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
          { x: 10, y: 15, size: 20, category: 'Category A' },
          { x: 20, y: 25, size: 35, category: 'Category A' },
          { x: 30, y: 35, size: 50, category: 'Category B' },
          { x: 40, y: 45, size: 65, category: 'Category B' }
        ]
      case 'pie':
        return [
          { category: 'Category A', value: 30 },
          { category: 'Category B', value: 25 },
          { category: 'Category C', value: 20 },
          { category: 'Category D', value: 15 },
          { category: 'Category E', value: 10 }
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
      case 'chord':
        return [
          { source: 'Beijing', target: 'Shanghai', value: 25 },
          { source: 'Beijing', target: 'Guangzhou', value: 18 },
          { source: 'Shanghai', target: 'Guangzhou', value: 22 },
          { source: 'Shanghai', target: 'Shenzhen', value: 15 },
          { source: 'Guangzhou', target: 'Shenzhen', value: 20 },
          { source: 'Shenzhen', target: 'Beijing', value: 12 }
        ]
      case 'node_link':
        return [
          { node: 'A', x: 10, y: 20, group: 'Group 1', size: 30 },
          { node: 'B', x: 30, y: 40, group: 'Group 1', size: 25 },
          { node: 'C', x: 50, y: 30, group: 'Group 2', size: 35 },
          { node: 'D', x: 70, y: 60, group: 'Group 2', size: 20 },
          { node: 'E', x: 90, y: 10, group: 'Group 3', size: 40 },
          { source: 'A', target: 'B', value: 1 },
          { source: 'B', target: 'C', value: 1 },
          { source: 'C', target: 'D', value: 1 },
          { source: 'D', target: 'E', value: 1 },
          { source: 'A', target: 'E', value: 1 }
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

  // Get data format description
  const getDataFormatDescription = (type) => {
    switch (type) {
      case 'bar':
        return 'Format: Array of objects, each containing x (category) and y (value) fields'
      case 'line':
        return 'Format: Array of objects, each containing x (time/category) and y (value) fields'
      case 'scatter':
      case 'bubble':
        return 'Format: Array of objects, each containing x (X-axis), y (Y-axis), size (optional), category (optional) fields'
      case 'pie':
        return 'Format: Array of objects, each containing category and value fields'
      case 'heatmap':
        return 'Format: Array of objects, each containing x (X-axis), y (Y-axis) and value fields'
      case 'treemap':
        return 'Format: Array of objects, each containing category and size fields'
      case 'chord':
        return 'Format: Array of objects, each containing source, target and value (connection strength) fields'
      case 'node_link':
        return 'Format: Array of objects, containing node data (node, x, y, group, size) and connection data (source, target, value)'
      default:
        return 'Format: Array of objects, each containing x (X-axis) and y (Y-axis) fields'
    }
  }

  // Validate JSON format
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
        setErrorMessage('Data must be in array format')
        return null
      }
      setIsValid(true)
      setErrorMessage('')
      return parsed
    } catch (error) {
      setIsValid(false)
      setErrorMessage(`JSON format error: ${error.message}`)
      return null
    }
  }

  // Handle JSON text changes
  const handleJsonChange = (e) => {
    const text = e.target.value
    setJsonText(text)
    setIsUserEditing(true)
    const parsed = validateJSON(text)
    if (parsed !== null) {
      onChange?.(parsed)
    }
  }

  // Initialize data
  useEffect(() => {
    // If user is editing, do not override user input
    if (isUserEditing) {
      return
    }
    
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
  }, [value, chartType, onChange, isUserEditing])

  // Reset to default data
  const resetToDefault = () => {
    const defaultData = getDefaultData(chartType)
    setJsonText(JSON.stringify(defaultData, null, 2))
    setIsValid(true)
    setErrorMessage('')
    setIsUserEditing(false) // Reset editing state
    onChange?.(defaultData)
    message.success('Reset to default data')
  }

  // Copy JSON to clipboard
  const copyToClipboard = () => {
    navigator.clipboard.writeText(jsonText).then(() => {
      message.success('JSON copied to clipboard')
    }).catch(() => {
      message.error('Copy failed')
    })
  }

  // Import JSON file
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
              message.error('File content must be in array format')
              return
            }
            setJsonText(JSON.stringify(parsed, null, 2))
            setIsValid(true)
            setErrorMessage('')
            setIsUserEditing(false) // Reset editing state
            onChange?.(parsed)
            message.success('JSON file imported successfully')
          } catch (error) {
            message.error('JSON file format error')
          }
        }
        reader.readAsText(file)
      }
    }
    input.click()
  }

  // Export JSON file
  const exportJSON = () => {
    if (!jsonText.trim()) {
      message.warning('No data to export')
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
    message.success('JSON file exported successfully')
  }

  return (
    <div>
      {/* Data format description */}
      <Card size="small" style={{ marginBottom: 8 }}>
        <div style={{ fontSize: '12px', color: '#666' }}>
          <Text strong>Data Format Description:</Text>
          <br />
          {getDataFormatDescription(chartType)}
        </div>
      </Card>

      {/* Operation buttons */}
      <Space style={{ marginBottom: 8 }}>
        <Tooltip title="Reset to default data">
          <Button size="small" icon={<ReloadOutlined />} onClick={resetToDefault}>
            Reset
          </Button>
        </Tooltip>
        <Tooltip title="Copy JSON to clipboard">
          <Button size="small" icon={<CopyOutlined />} onClick={copyToClipboard}>
            Copy
          </Button>
        </Tooltip>
        <Button size="small" icon={<UploadOutlined />} onClick={importJSON}>
          Import JSON
        </Button>
        <Button size="small" icon={<DownloadOutlined />} onClick={exportJSON}>
          Export JSON
        </Button>
      </Space>

      {/* Error message */}
      {!isValid && (
        <Alert
          message="JSON Format Error"
          description={errorMessage}
          type="error"
          showIcon
          style={{ marginBottom: 8 }}
        />
      )}

      {/* JSON input box */}
      <TextArea
        value={jsonText}
        onChange={handleJsonChange}
        placeholder="Please enter JSON format data..."
        rows={12}
        style={{
          fontFamily: 'Monaco, Menlo, Consolas, monospace',
          fontSize: '12px',
          borderColor: isValid ? undefined : '#ff4d4f'
        }}
      />

      {/* Data preview */}
      {isValid && jsonText.trim() && (
        <div style={{ marginTop: 8, fontSize: '12px', color: '#666' }}>
          <Text>Data Preview: {JSON.parse(jsonText).length} records</Text>
        </div>
      )}
    </div>
  )
}

export default DataTableEditor
