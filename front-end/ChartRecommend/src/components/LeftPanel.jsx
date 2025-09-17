import {Input, Typography, theme, Button, message, Slider, Space, Select} from 'antd'
import ChartHistory from './ChartHistory'
import Retrieval from "./Retrieval.jsx";
import {useEffect, useState, useRef, forwardRef, useImperativeHandle} from "react";


const {TextArea} = Input
const {Title} = Typography

const processChartData = async (item) => {
    try {
        // If there is a PNG image, return directly
        if (item.image) {
            return item;
        }
        
        // If there is SVG, process it to make it responsive
        if (item.svg) {
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
        }

        return item
    } catch (error) {
        console.error(`Failed to process chart data for ${item.chartType}:`, error);
        return item;
    }
};

const LeftPanel = forwardRef(({historyItems = [], onSelectHistory, onClearHistory, onDeleteHistory, onReorderHistory, onChartSelect, onRefreshHistory}, ref) => {
    const {token} = theme.useToken()

    const [query, setQuery] = useState("")
    const [sparse, setSparse] = useState([])
    const [dense, setDense] = useState([])
    
    // 自动输入相关状态
    const [isTyping, setIsTyping] = useState(false)
    const [typingSpeed, setTypingSpeed] = useState(5) // 毫秒
    const [selectedPreset, setSelectedPreset] = useState('')
    const [customText, setCustomText] = useState('')
    const [typingProgress, setTypingProgress] = useState({ current: 0, total: 0 })
    const typingIntervalRef = useRef(null)
    const currentIndexRef = useRef(0)
    const targetTextRef = useRef('')
    
    // 预设文本选项
    const presetTexts = [
        {
            label: '销售数据分析', 
            value: 'sales_analysis', 
            text: `A data visualization of 250 restaurants reveals key patterns in the relationship between pricing, ratings, and foot traffic across different cuisine types. Mid-priced establishments ($15-35 per entrée) create a "sweet spot," clustering around 4.2-4.6 star ratings where customers perceive optimal value. Budget restaurants under $12 show dramatic rating variation (2.8-4.8 stars), indicating execution trumps price at the lower end. 
Notable outliers include high- end restaurants($80 + per entrée) maintaining perfect 4.9 - 5.0 ratings with strong traffic, demonstrating successful premium positioning.Asian fusion restaurants exhibit remarkable consistency(4.3 - 4.7 stars) across all price ranges, while traditional American diners suffer rating declines when pricing exceeds $25, suggesting customer resistance to premium comfort food pricing.
Fast - casual chains dominate high - volume traffic in the $8 - 18 range, though three independent pizza shops break this pattern by combining substantial foot traffic with mid - tier pricing through community loyalty and strategic college - area locations.`
        },
        { label: '用户行为分析', value: 'user_behavior', text: '分析用户在我们平台上的行为模式，包括页面访问量、停留时间、点击率等指标。请提供热力图显示用户最常访问的页面区域，以及漏斗图展示用户转化流程。' },
        { label: '财务报告', value: 'financial_report', text: '生成2023年财务报告的可视化图表，包括收入、支出、利润的月度对比。需要饼图显示各项支出的占比，以及散点图分析收入与支出的相关性。' },
        { label: '市场调研', value: 'market_research', text: '展示市场调研结果，包括不同年龄段用户的偏好分布、地域市场表现、竞品对比分析。请使用雷达图展示各产品维度的评分，以及桑基图显示用户流向。' },
        { label: '运营数据', value: 'operation_data', text: '分析运营数据，包括日活用户数、留存率、转化率等关键指标。需要时间序列图显示趋势变化，以及气泡图展示不同渠道的效果对比。' }
    ]

    // 自动输入功能 - 可以通过代码调用
    const startTyping = (text, speed = typingSpeed) => {
        if (isTyping) return
        
        if (!text || !text.trim()) {
            message.warning('请输入要自动输入的文本')
            return
        }
        
        setIsTyping(true)
        setQuery('') // 清空当前内容
        targetTextRef.current = text
        currentIndexRef.current = 0
        setTypingProgress({ current: 0, total: text.length })
        
        // 立即输入第一个字符
        if (text.length > 0) {
            setQuery(text[0])
            currentIndexRef.current = 1
            setTypingProgress({ current: 1, total: text.length })
        }
        
        // 从第二个字符开始定时输入
        typingIntervalRef.current = setInterval(() => {
            if (currentIndexRef.current < targetTextRef.current.length) {
                setQuery(prev => prev + targetTextRef.current[currentIndexRef.current])
                currentIndexRef.current++
                setTypingProgress({ 
                    current: currentIndexRef.current, 
                    total: targetTextRef.current.length 
                })
            } else {
                stopTyping()
            }
        }, speed)
    }
    
    const stopTyping = () => {
        if (typingIntervalRef.current) {
            clearInterval(typingIntervalRef.current)
            typingIntervalRef.current = null
        }
        setIsTyping(false)
        setTypingProgress({ current: 0, total: 0 })
    }
    
    // 使用预设文本进行自动输入
    const typePresetText = (presetValue, speed = typingSpeed) => {
        const preset = presetTexts.find(p => p.value === presetValue)
        if (preset) {
            startTyping(preset.text, speed)
        } else {
            message.warning('未找到指定的预设文本')
        }
    }
    
    // 使用自定义文本进行自动输入
    const typeCustomText = (text, speed = typingSpeed) => {
        startTyping(text, speed)
    }
    
    // 暴露给父组件的方法
    useImperativeHandle(ref, () => ({
        // 使用预设文本进行自动输入
        typePresetText: (presetValue, speed) => typePresetText(presetValue, speed),
        // 使用自定义文本进行自动输入
        typeCustomText: (text, speed) => typeCustomText(text, speed),
        // 开始自动输入
        startTyping: (text, speed) => startTyping(text, speed),
        // 停止自动输入
        stopTyping: () => stopTyping(),
        // 获取当前输入状态
        isTyping: isTyping,
        // 获取预设文本列表
        getPresetTexts: () => presetTexts,
        // 设置输入速度
        setTypingSpeed: (speed) => setTypingSpeed(speed)
    }))
    
    // 清理定时器
    useEffect(() => {
        return () => {
            if (typingIntervalRef.current) {
                clearInterval(typingIntervalRef.current)
            }
        }
    }, [])
   
    const getSparse = async () => {
        // Validate that query is not empty
        if (!query || query.trim() === '') {
            message.warning('Please enter query content')
            return
        }

        const response = await fetch('http://10.12.42.176:11011/sparse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query.trim()
            }),
        })
        let responseList = await response.json()
        // Wait for all SVG processing to complete
        responseList = await Promise.all(responseList.map(item => processChartData(item)));
        setSparse(responseList)
        console.log('sparse')
        console.log(responseList)
    }

    const getDense = async () => {
        // Validate that query is not empty
        if (!query || query.trim() === '') {
            message.warning('Please enter query content')
            return
        }

        const response = await fetch('http://10.12.42.176:11011/dense', {
            method: 'POST',  // Set request method to POST
            headers: {
                'Content-Type': 'application/json',  // Tell server the request body data type is JSON
            },
            body: JSON.stringify({
                query: query.trim()
            }),  // Convert request body data to JSON string
        })
        let responseList = await response.json()
        responseList = await Promise.all(responseList.map(item => processChartData(item)))
        setDense(responseList)
        console.log('dense')
        console.log(dense)
    }

    return (
        <div style={{display: 'flex', flexDirection: 'column', gap: 12, height: '100%'}}>
            <div className="app-left-top">
                <Title level={5} style={{marginBottom: 8}}>Text Input</Title>
                <TextArea
                    placeholder="Enter text here..."
                    autoSize={{minRows: 4, maxRows: 4}}
                    style={{height: '100%'}}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <Button 
                    type="primary" 
                    size="small" 
                    disabled={!query || query.trim() === ''}
                    onClick={() => { getDense(); getSparse(); }}
                >
                    Recommend
                </Button>
            </div>
            <div
                className="app-left-bottom"
                style={{
                    border: `1px solid ${token.colorBorderSecondary}`,
                    borderRadius: 8,
                    padding: 12,
                    display: "grid",
                    gridTemplateRows: "auto 1fr", // First row is title, remaining part for content
                }}
            >
                <Title level={5} style={{marginTop: 0}}>Display Area</Title>

                {/* Three retrieval block containers */}
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
                {/* <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8}}>
                    <Title level={5} style={{marginTop: 0, marginBottom: 0}}>History</Title>
                    <Button 
                        size="small" 
                        onClick={onRefreshHistory}
                        style={{fontSize: '12px'}}
                    >
                        刷新
                    </Button>
                </div> */}
                <div style={{flex: 1, minHeight: 0}}>
                    <ChartHistory items={historyItems} onSelect={onSelectHistory} onClear={onClearHistory}
                                  onDelete={onDeleteHistory} onReorder={onReorderHistory}/>
                </div>
            </div>
        </div>
    )
})

export default LeftPanel 