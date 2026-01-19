import { useRef, useState } from 'react'
import '../index.css'

interface UploadZoneProps {
    onFileSelect: (file: File) => void
}

export default function UploadZone({ onFileSelect }: UploadZoneProps) {
    const [isDragging, setIsDragging] = useState(false)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(true)
    }

    const handleDragLeave = () => {
        setIsDragging(false)
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            onFileSelect(e.dataTransfer.files[0])
        }
    }

    return (
        <div
            className={`glass-panel`}
            style={{
                padding: '3rem',
                border: isDragging ? '2px dashed var(--primary)' : '2px dashed rgba(255,255,255,0.1)',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                background: isDragging ? 'rgba(79, 70, 229, 0.1)' : 'rgba(30, 41, 59, 0.7)'
            }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
        >
            <input
                type="file"
                ref={fileInputRef}
                onChange={(e) => e.target.files?.[0] && onFileSelect(e.target.files[0])}
                style={{ display: 'none' }}
                accept="image/*"
            />

            <div style={{ marginBottom: '1.5rem' }}>
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--primary)' }}>
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
            </div>

            <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>点击或拖拽上传试卷</h3>
            <p style={{ color: 'var(--text-muted)' }}>支持 JPG, PNG 格式</p>
        </div>
    )
}
