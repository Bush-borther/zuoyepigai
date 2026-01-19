import '../index.css'

interface ResultViewerProps {
    result: {
        original_image: string
        graded_image: string
        pdf_url: string
        details: any[]
    }
    onReset: () => void
}

export default function ResultViewer({ result, onReset }: ResultViewerProps) {
    const backendUrl = "http://localhost:8000" // Should be env var

    const handlePrint = () => {
        // Open PDF in new window which usually triggers browser PDF viewer with print
        window.open(`${backendUrl}${result.pdf_url}`, '_blank')
    }

    return (
        <div className="glass-panel" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2 style={{ fontSize: '1.5rem' }}>批改结果</h2>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button
                        onClick={onReset}
                        style={{
                            background: 'transparent',
                            color: 'var(--text-muted)',
                            border: '1px solid var(--text-muted)',
                            padding: '0.5rem 1rem',
                            borderRadius: 'var(--radius-sm)'
                        }}
                    >
                        继续批改
                    </button>
                    <button className="btn-primary" onClick={handlePrint}>
                        打印 / 下载 PDF
                    </button>
                </div>
            </div>

            <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                <div style={{ flex: 1, minWidth: '300px' }}>
                    <h3 style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>批改详情</h3>
                    <div style={{
                        background: 'rgba(0,0,0,0.2)',
                        borderRadius: 'var(--radius-md)',
                        padding: '1rem',
                        maxHeight: '500px',
                        overflowY: 'auto'
                    }}>
                        <img
                            src={`${backendUrl}${result.graded_image}`}
                            alt="Graded Result"
                            style={{ width: '100%', borderRadius: 'var(--radius-sm)' }}
                        />
                    </div>
                </div>
            </div>
        </div>
    )
}
