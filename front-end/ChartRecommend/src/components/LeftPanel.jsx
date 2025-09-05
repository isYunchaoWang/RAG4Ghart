import {Input, Typography, theme, Button} from 'antd'
import ChartHistory from './ChartHistory'
import Retrieval from "./Retrieval.jsx";
import {useEffect, useState} from "react";


const {TextArea} = Input
const {Title} = Typography

const processSvg = async (item) => {
    try {
        // 处理大型SVG使其响应式
        const widthMatch = item.svg.match(/width="(\d+)"/);
        const heightMatch = item.svg.match(/height="(\d+)"/);

        if (widthMatch && heightMatch) {
            const originalWidth = widthMatch[1];
            const originalHeight = heightMatch[1];

            item.svg = item.svg
                .replace(/width="[^"]*"/, 'width="100%"')
                .replace(/height="[^"]*"/, 'height="100%"')
                .replace(/<svg([^>]*)>/, `<svg$1 viewBox="0 0 ${originalWidth} ${originalHeight}" preserveAspectRatio="xMidYMid meet">`);
        }

        return item
    } catch (error) {
        console.error(`Failed to fetch SVG for ${item.chartType}:`, error);
    }
};

function LeftPanel({historyItems = [], onSelectHistory, onClearHistory, onDeleteHistory, onChartSelect}) {
    const {token} = theme.useToken()

    const [query, setQuery] = useState("")

    const [sparse, setSparse] = useState([
        {chartType: "bar", svg: "bar"},
        {chartType: "bubble", svg: "bubble"},
        {chartType: "chord", svg: "chord"},
        {chartType: "funnel", svg: "funnel"},
        {chartType: "pie", svg: "pie"},
    ])
    const [dense, setDense] = useState([
        {chartType: "bubble", score: 0.9, svg: "bubble"},
        {chartType: "funnel", score: 0.8, svg: "funnel"},
        {chartType: "bar", score: 0.7, svg: "bar"},
        {chartType: "treemap", score: 0.6, svg: "treemap"},
        {chartType: "pie", score: 0.5, svg: "pie"},
    ])

    const getSparse = () => {

    }

    const getDense = async () => {
        const response = await fetch('http://localhost:8000', {
            method: 'POST',  // 设置请求方法为 POST
            headers: {
                'Content-Type': 'application/json',  // 告诉服务器请求体的数据类型是 JSON
            },
            body: JSON.stringify({
                query: query
            }),  // 将请求体数据转换为 JSON 字符串
        })
        const responseList = await response.json()
        responseList.map(item => processSvg(item));
        setDense(responseList)
        console.log(dense)
    }

    return (
        <div style={{display: 'flex', flexDirection: 'column', gap: 12, height: '100%'}}>
            <div className="app-left-top">
                <Title level={5} style={{marginBottom: 8}}>文本输入</Title>
                <TextArea
                    placeholder="在这里输入文本..."
                    autoSize={{minRows: 3, maxRows: 6}}
                    style={{height: '100%'}}
                    value={query}
                />
                <Button type="primary" size="small" onClick={getDense}>推荐</Button>
            </div>
            <div
                className="app-left-bottom"
                style={{
                    border: `1px solid ${token.colorBorderSecondary}`,
                    borderRadius: 8,
                    padding: 12,
                    display: "grid",
                    gridTemplateRows: "auto 1fr", // 第一行是标题，剩下部分给内容
                }}
            >
                <Title level={5} style={{marginTop: 0}}>信息展示区</Title>

                {/* 三个检索块容器 */}
                <Retrieval sparse={sparse} dense={dense} onChartSelect={onChartSelect}/>
            </div>
            <div className="app-left-history" style={{
                border: `1px solid ${token.colorBorderSecondary}`,
                borderRadius: 8,
                padding: 12,
                display: 'flex',
                flexDirection: 'column',
                minHeight: 0
            }}>
                <Title level={5} style={{marginTop: 0}}>历史记录</Title>
                <div style={{flex: 1, minHeight: 0}}>
                    <ChartHistory items={historyItems} onSelect={onSelectHistory} onClear={onClearHistory}
                                  onDelete={onDeleteHistory}/>
                </div>
            </div>
        </div>
    )
}

export default LeftPanel 