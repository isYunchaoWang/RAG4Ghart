import {theme, Typography} from 'antd'

const {Title} = Typography

const fusion = (sparse, dense, k = 60) => {
    const fusionMap = new Map();

    // Process sparse retrieval results (based on ranking)
    sparse.forEach((item, index) => {
        const rank = index + 1;
        fusionMap.set(item.image || item.svg, {
            chartType: item.chartType,
            image: item.image,
            svg: item.svg,
            sparseScore: item.score,
            denseScore: 0,
            sparseRank: rank,
            denseRank: Infinity,
            rrfScore: 1 / (k + rank)
        });
    });

    // Process dense retrieval results
    dense.forEach((item, index) => {
        const rank = index + 1;
        if (fusionMap.has(item.image || item.svg)) {
            const existing = fusionMap.get(item.image || item.svg);
            existing.denseScore = item.score;
            existing.denseRank = rank;
            existing.rrfScore += 1 / (k + rank);
        } else {
            fusionMap.set(item.image || item.svg, {
                chartType: item.chartType,
                image: item.image,
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
            image: item.image,
            svg: item.svg,
            score: item.rrfScore.toFixed(3) // Display RRF score
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
            {/* Sparse Retrieval */}
            <div style={{
                border: `1px solid ${token.colorBorderSecondary}`,
                borderRadius: 8,
                padding: 8,
                display: "grid",
                gridTemplateRows: "auto 1fr",
                gap: 8
            }}>
                <Title level={5} style={{marginTop: 0}}>Sparse Retrieval</Title>
                <div style={{display: "grid", gridTemplateRows: "repeat(5, 1fr)", gap: 6}}>
                    {sparse.map(item => (
                        <div 
                            key={item.image || item.svg} 
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
                            {/* Render PNG image */}
                            {item.image ? (
                                <img
                                    src={item.image}
                                    alt={item.chartType}
                                    style={{
                                        width: '100%',
                                        height: '180px',
                                        objectFit: 'contain',
                                        borderRadius: '4px',
                                        background: '#ffffff'
                                    }}
                                />
                            ) : item.svg ? (
                                <div
                                    className="svg-container"
                                    dangerouslySetInnerHTML={{__html: item.svg}}
                                    style={{
                                        width: '100%',
                                        height: '180px',
                                        borderRadius: '4px',
                                        overflow: 'hidden',
                                        display: 'flex',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                    }}
                                />
                            ) : (
                                <div style={{
                                    width: '100%',
                                    height: '180px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    background: '#ffffff',
                                    borderRadius: '4px',
                                    color: '#999'
                                }}>
                                    No Preview
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Dense Retrieval */}
            <div style={{
                border: `1px solid ${token.colorBorderSecondary}`,
                borderRadius: 8,
                padding: 8,
                display: "grid",
                gridTemplateRows: "auto 1fr",
                gap: 8
            }}>
                <Title level={5} style={{marginTop: 0}}>Dense Retrieval</Title>
                <div style={{display: "grid", gridTemplateRows: "repeat(5, 1fr)", gap: 6}}>
                    {dense.map(item => (
                        <div 
                            key={item.image || item.svg} 
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
                            {/* Render PNG image */}
                            {item.image ? (
                                <img
                                    src={item.image}
                                    alt={item.chartType}
                                    style={{
                                        width: '100%',
                                        height: '180px',
                                        objectFit: 'contain',
                                        borderRadius: '4px',
                                        background: '#ffffff'
                                    }}
                                />
                            ) : item.svg ? (
                                <div
                                    className="svg-container"
                                    dangerouslySetInnerHTML={{__html: item.svg}}
                                    style={{
                                        width: '100%',
                                        height: '180px',
                                        borderRadius: '4px',
                                        overflow: 'hidden',
                                        display: 'flex',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                    }}
                                />
                            ) : (
                                <div style={{
                                    width: '100%',
                                    height: '180px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    background: '#ffffff',
                                    borderRadius: '4px',
                                    color: '#999'
                                }}>
                                    No Preview
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Hybrid Retrieval */}
            <div style={{
                border: `1px solid ${token.colorBorderSecondary}`,
                borderRadius: 8,
                padding: 8,
                display: "grid",
                gridTemplateRows: "auto 1fr",
                gap: 8
            }}>
                <Title level={5} style={{marginTop: 0}}>RRF Fusion</Title>
                <div style={{display: "grid", gridTemplateRows: "repeat(5, 1fr)", gap: 6}}>
                    {fusion(sparse, dense).map(item => (
                        <div 
                            key={item.image || item.svg} 
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
                            {/* Render PNG image */}
                            {item.image ? (
                                <img
                                    src={item.image}
                                    alt={item.chartType}
                                    style={{
                                        width: '100%',
                                        height: '180px',
                                        objectFit: 'contain',
                                        borderRadius: '4px',
                                        background: '#ffffff'
                                    }}
                                />
                            ) : item.svg ? (
                                <div
                                    className="svg-container"
                                    dangerouslySetInnerHTML={{__html: item.svg}}
                                    style={{
                                        width: '100%',
                                        height: '180px',
                                        borderRadius: '4px',
                                        overflow: 'hidden',
                                        display: 'flex',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                    }}
                                />
                            ) : (
                                <div style={{
                                    width: '100%',
                                    height: '180px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    background: '#ffffff',
                                    borderRadius: '4px',
                                    color: '#ffffff'
                                }}>
                                    No Preview
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default Retrieval