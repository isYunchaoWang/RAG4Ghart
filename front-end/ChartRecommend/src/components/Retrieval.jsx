import {theme, Typography} from 'antd'

const {Title} = Typography

const fusion = (sparse, dense, k = 60) => {
    const fusionMap = new Map();

    // 处理稀疏检索结果（基于排名）
    sparse.forEach((item, index) => {
        const rank = index + 1;
        fusionMap.set(item.svg, {
            chartType: item.chartType,
            svg: item.svg,
            sparseScore: item.score,
            denseScore: 0,
            sparseRank: rank,
            denseRank: Infinity,
            rrfScore: 1 / (k + rank)
        });
    });

    // 处理稠密检索结果
    dense.forEach((item, index) => {
        const rank = index + 1;
        if (fusionMap.has(item.svg)) {
            const existing = fusionMap.get(item.svg);
            existing.denseScore = item.score;
            existing.denseRank = rank;
            existing.rrfScore += 1 / (k + rank);
        } else {
            fusionMap.set(item.svg, {
                chartType: item.chartType,
                svg: item.svg,
                sparseScore: 0,
                denseScore: item.score,
                sparseRank: Infinity,
                denseRank: rank,
                rrfScore: 1 / (k + rank)
            });
        }
    });

    return Array.from(fusionMap.values())
        .sort((a, b) => b.rrfScore - a.rrfScore)
        .slice(0, 5)
        .map(item => ({
            chartType: item.chartType,
            svg: item.svg,
            score: item.rrfScore.toFixed(3) // 显示RRF分数
        }));
};

function Retrieval({sparse = [], dense = [], onChartSelect}) {
    const {token} = theme.useToken()
    
    const handleChartClick = (chartType) => {
        if (onChartSelect) {
            onChartSelect(chartType)
        }
    }
    
    return (
        <div style={{display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12}}>
            {/* 稀疏检索 */}
            <div style={{
                border: `1px solid ${token.colorBorderSecondary}`,
                borderRadius: 8,
                padding: 8,
                display: "grid",
                gridTemplateRows: "auto 1fr",
                gap: 8
            }}>
                <Title level={5} style={{marginTop: 0}}>稀疏检索</Title>
                <div style={{display: "grid", gridTemplateRows: "repeat(5, 1fr)", gap: 6}}>
                    {sparse.map(item => (
                        <div 
                            key={item.svg} 
                            style={{
                                border: `1px solid ${token.colorBorderSecondary}`, 
                                borderRadius: 4,
                                padding: 4,
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                                '&:hover': {
                                    borderColor: token.colorPrimary,
                                    boxShadow: `0 2px 8px ${token.colorPrimary}20`
                                }
                            }}
                            onClick={() => handleChartClick(item.chartType)}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.borderColor = token.colorPrimary
                                e.currentTarget.style.boxShadow = `0 2px 8px ${token.colorPrimary}20`
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.borderColor = token.colorBorderSecondary
                                e.currentTarget.style.boxShadow = 'none'
                            }}
                        >
                            <Title level={5} style={{marginTop: 0}}>{item.chartType}</Title>
                            {/* 渲染 SVG 字符串 */}
                            {item.svg && (
                                <div
                                    className="svg-container"
                                    dangerouslySetInnerHTML={{__html: item.svg}}
                                    style={{
                                        width: '100%',
                                        height: '180px', // 稍微调小一点给标题留空间
                                        borderRadius: '4px',
                                        overflow: 'hidden',
                                        display: 'flex',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                    }}
                                />
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* 稠密检索 */}
            <div style={{
                border: `1px solid ${token.colorBorderSecondary}`,
                borderRadius: 8,
                padding: 8,
                display: "grid",
                gridTemplateRows: "auto 1fr",
                gap: 8
            }}>
                <Title level={5} style={{marginTop: 0}}>稠密检索</Title>
                <div style={{display: "grid", gridTemplateRows: "repeat(5, 1fr)", gap: 6}}>
                    {dense.map(item => (
                        <div 
                            key={item.svg} 
                            style={{
                                border: `1px solid ${token.colorBorderSecondary}`, 
                                borderRadius: 4,
                                padding: 4,
                                cursor: 'pointer',
                                transition: 'all 0.2s ease'
                            }}
                            onClick={() => handleChartClick(item.chartType)}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.borderColor = token.colorPrimary
                                e.currentTarget.style.boxShadow = `0 2px 8px ${token.colorPrimary}20`
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.borderColor = token.colorBorderSecondary
                                e.currentTarget.style.boxShadow = 'none'
                            }}
                        >
                            <Title level={5} style={{marginTop: 0}}>{item.chartType}</Title>
                            {/* 渲染 SVG 字符串 */}
                            {item.svg && (
                                <div
                                    className="svg-container"
                                    dangerouslySetInnerHTML={{__html: item.svg}}
                                    style={{
                                        width: '100%',
                                        height: '180px', // 稍微调小一点给标题留空间
                                        borderRadius: '4px',
                                        overflow: 'hidden',
                                        display: 'flex',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                    }}
                                />
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* 混合检索 */}
            <div style={{
                border: `1px solid ${token.colorBorderSecondary}`,
                borderRadius: 8,
                padding: 8,
                display: "grid",
                gridTemplateRows: "auto 1fr",
                gap: 8
            }}>
                <Title level={5} style={{marginTop: 0}}>RRF融合</Title>
                <div style={{display: "grid", gridTemplateRows: "repeat(5, 1fr)", gap: 6}}>
                    {fusion(sparse, dense).map(item => (
                        <div 
                            key={item.svg} 
                            style={{
                                border: `1px solid ${token.colorBorderSecondary}`, 
                                borderRadius: 4,
                                padding: 4,
                                cursor: 'pointer',
                                transition: 'all 0.2s ease'
                            }}
                            onClick={() => handleChartClick(item.chartType)}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.borderColor = token.colorPrimary
                                e.currentTarget.style.boxShadow = `0 2px 8px ${token.colorPrimary}20`
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.borderColor = token.colorBorderSecondary
                                e.currentTarget.style.boxShadow = 'none'
                            }}
                        >
                            <Title level={5} style={{marginTop: 0}}>{item.chartType}</Title>
                            {/* 渲染 SVG 字符串 */}
                            {item.svg && (
                                <div
                                    className="svg-container"
                                    dangerouslySetInnerHTML={{__html: item.svg}}
                                    style={{
                                        width: '100%',
                                        height: '180px', // 稍微调小一点给标题留空间
                                        borderRadius: '4px',
                                        overflow: 'hidden',
                                        display: 'flex',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                    }}
                                />
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default Retrieval