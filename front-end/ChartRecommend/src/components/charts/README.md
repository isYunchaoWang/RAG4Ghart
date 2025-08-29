# 图表组件架构说明

## 概述

为了提高代码的可维护性和扩展性，我们将图表编辑器重构为组件化架构。每种图表类型都有自己独立的组件，这样可以：

1. **避免样式配置冲突**：每种图表类型可以有自己的样式配置逻辑
2. **提高代码可读性**：每个组件的职责更加明确
3. **便于扩展**：新增图表类型只需要创建新的组件
4. **更好的类型安全**：每种图表类型可以有特定的配置

## 组件结构

```
charts/
├── ChartFactory.jsx      # 图表组件工厂，根据类型选择对应组件
├── BarChart.jsx          # 柱状图组件
├── LineChart.jsx         # 线图组件
├── PieChart.jsx          # 饼图组件
├── ScatterChart.jsx      # 散点图组件
├── HeatmapChart.jsx      # 热力图组件
├── AreaChart.jsx         # 面积图组件
├── BoxChart.jsx          # 箱线图组件
├── GenericChart.jsx      # 通用图表组件（后备方案）
└── README.md            # 本文档
```

## 组件映射

### 专用组件
- **BarChart**: `bar`, `stacked_bar`
- **LineChart**: `line`, `radar`
- **PieChart**: `pie`, `sunburst`
- **ScatterChart**: `point`, `scatter`, `bubble`, `fill_bubble`
- **HeatmapChart**: `heatmap`, `treemap`, `treemap_D3`, `sankey`
- **AreaChart**: `stacked_area`, `stream`, `ridgeline`, `violin`
- **BoxChart**: `box`

### 通用组件
- **GenericChart**: 所有其他图表类型（作为后备方案）

## 组件接口

所有图表组件都遵循相同的接口：

```jsx
function ChartComponent({ 
  chartType,      // 图表类型
  title,          // 标题
  description,    // 描述
  width,          // 宽度
  height,         // 高度
  formValues,     // 表单值（包含所有配置）
  dataValues,     // 数据值
  onEmbed         // 嵌入回调
}) {
  // 组件实现
}
```

## 样式配置

每种图表组件都支持以下样式配置：

### 基础样式
- **透明度** (`opacity`)
- **边框宽度** (`strokeWidth`)

### 特定样式
- **圆角半径** (`cornerRadius`) - 柱状图
- **点大小** (`pointSize`) - 散点图
- **线条宽度** (`lineWidth`) - 线图
- **线条样式** (`strokeDash`) - 线图
- **内半径** (`innerRadius`) - 饼图

### 轴配置
- **显示网格** (`showGrid`)

### 图例配置
- **显示图例** (`showLegend`)
- **图例位置** (`legendPosition`)
- **图例方向** (`legendOrientation`)

### 字体配置
- **字体族** (`fontFamily`)
- **字体大小** (`fontSize`)



## 字体配置说明

每种图表组件都支持独立的字体配置，包括：

1. **标题字体** - 图表主标题
2. **轴标签字体** - X轴和Y轴的标签
3. **轴标题字体** - X轴和Y轴的标题
4. **图例标签字体** - 图例中的标签
5. **图例标题字体** - 图例的标题

这样可以避免不同图表元素之间的字体配置相互覆盖。

## 扩展新图表类型

要添加新的图表类型，请按以下步骤操作：

1. **创建专用组件**（如果需要特殊处理）：
   ```jsx
   // NewChartType.jsx
   import React from 'react'
   import { VegaEmbed } from 'react-vega'
   
   function buildNewChartTypeSpec({ title, description, width, height, formValues, dataValues }) {
     // 实现特定的图表配置逻辑
   }
   
   function NewChartType({ title, description, width, height, formValues, dataValues, onEmbed }) {
     const spec = buildNewChartTypeSpec({ title, description, width, height, formValues, dataValues })
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
   
   export default NewChartType
   ```

2. **更新 ChartFactory**：
   ```jsx
   import NewChartType from './NewChartType'
   
   const CHART_COMPONENTS = {
     // ... 现有映射
     new_chart_type: NewChartType,
   }
   ```

3. **或者使用通用组件**：
   如果新图表类型不需要特殊处理，可以直接在 `GenericChart` 中添加支持。

## 优势

1. **模块化**：每种图表类型独立维护
2. **可扩展**：易于添加新的图表类型
3. **可测试**：每个组件可以独立测试
4. **性能优化**：可以针对特定图表类型进行优化
5. **样式隔离**：避免不同图表类型的样式配置冲突
