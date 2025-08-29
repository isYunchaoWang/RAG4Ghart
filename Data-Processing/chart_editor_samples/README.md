# 图表编辑器数据表格样例总览

本目录包含各种图表类型的数据表格样例和填写说明。

## 支持的图表类型

| 图表类型 | 文件名 | 描述 |
|---------|--------|------|
| box | box_sample.csv | 箱型图 - 显示数据分布情况 |
| violin | violin_sample.csv | 小提琴图 - 显示数据密度分布 |
| bar | bar_sample.csv | 柱状图 - 比较不同类别的数值 |
| scatter | scatter_sample.csv | 散点图 - 显示两个变量间的关系 |
| line | line_sample.csv | 折线图 - 显示数据变化趋势 |
| pie | pie_sample.csv | 饼图 - 显示整体中各部分占比 |
| heatmap | heatmap_sample.csv | 热力图 - 显示两个分类变量间的关系强度 |
| bubble | bubble_sample.csv | 气泡图 - 散点图的扩展，用气泡大小表示第三个变量 |
| histogram | histogram_sample.csv | 直方图 - 显示数据的分布情况 |
| area | area_sample.csv | 面积图 - 折线图的变体，填充折线下方区域 |
| stacked_bar | stacked_bar_sample.csv | 堆叠柱状图 - 显示每个类别中不同子类别的构成 |
| stacked_area | stacked_area_sample.csv | 堆叠面积图 - 显示多个系列随时间的变化趋势 |
| radar | radar_sample.csv | 雷达图 - 比较多个维度的数值 |
| funnel | funnel_sample.csv | 漏斗图 - 显示流程中各阶段的转化情况 |

## 使用方法

1. 选择对应的图表类型样例文件
2. 查看填写说明文档
3. 按照样例格式填写您的数据
4. 将数据导入图表编辑器

## 文件说明

- `*_sample.csv`: 数据表格样例文件
- `*_instructions.json`: 填写说明的JSON格式文件
- `*_README.md`: 详细的填写说明文档

## 注意事项

- 请严格按照样例格式填写数据
- 列名必须与样例完全一致
- 数据类型要正确（数值列不要包含文字）
- 确保数据的完整性和一致性
