import {Input, Typography, theme, Button, message} from 'antd'
import ChartHistory from './ChartHistory'
import Retrieval from "./Retrieval.jsx";
import {useEffect, useState} from "react";


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

function LeftPanel({historyItems = [], onSelectHistory, onClearHistory, onDeleteHistory, onChartSelect}) {
    const {token} = theme.useToken()

    const [query, setQuery] = useState("")

    const [sparse, setSparse] = useState([])
    const [dense, setDense] = useState([])

   
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
        console.log(responseList)
    }

    const getDense = async () => {
        // Validate that query is not empty
        if (!query || query.trim() === '') {
            message.warning('Please enter query content')
            return
        }

        const response = await fetch('http://localhost:8000', {
            method: 'POST',  // Set request method to POST
            headers: {
                'Content-Type': 'application/json',  // Tell server the request body data type is JSON
            },
            body: JSON.stringify({
                query: query.trim()
            }),  // Convert request body data to JSON string
        })
        const responseList = await response.json()
        responseList.map(item => processChartData(item));
        setDense(responseList)
        console.log(dense)
    }

    return (
        <div style={{display: 'flex', flexDirection: 'column', gap: 12, height: '100%'}}>
            <div className="app-left-top">
                <Title level={5} style={{marginBottom: 8}}>Text Input</Title>
                <TextArea
                    placeholder="Enter text here..."
                    autoSize={{minRows: 3, maxRows: 6}}
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
                <Title level={5} style={{marginTop: 0}}>Information Display Area</Title>

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
                <Title level={5} style={{marginTop: 0}}>History</Title>
                <div style={{flex: 1, minHeight: 0}}>
                    <ChartHistory items={historyItems} onSelect={onSelectHistory} onClear={onClearHistory}
                                  onDelete={onDeleteHistory}/>
                </div>
            </div>
        </div>
    )
}

export default LeftPanel 