import { useState, useEffect } from 'react'

interface SettingsModalProps {
    isOpen: boolean
    onClose: () => void
}

interface LLMConfig {
    apiKey: string
    baseUrl: string
    model: string
}

const STORAGE_KEY = 'llm_config'

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
    const [config, setConfig] = useState<LLMConfig>({
        apiKey: '',
        baseUrl: 'https://api.openai.com/v1',
        model: 'gpt-4o'
    })
    const [saving, setSaving] = useState(false)
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

    // 从 localStorage 加载配置
    useEffect(() => {
        const savedConfig = localStorage.getItem(STORAGE_KEY)
        if (savedConfig) {
            try {
                const parsed = JSON.parse(savedConfig)
                setConfig(parsed)

                // 自动发送到后端
                fetch('http://localhost:8000/api/config/llm', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        api_key: parsed.apiKey,
                        base_url: parsed.baseUrl,
                        model: parsed.model
                    })
                }).catch(err => console.error('Failed to restore config:', err))
            } catch (e) {
                console.error('Failed to parse saved config:', e)
            }
        }
    }, [])

    if (!isOpen) return null

    const handleSave = async () => {
        if (!config.apiKey.trim()) {
            setMessage({ type: 'error', text: '请输入 API Key' })
            return
        }

        setSaving(true)
        setMessage(null)

        try {
            const response = await fetch('http://localhost:8000/api/config/llm', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_key: config.apiKey,
                    base_url: config.baseUrl,
                    model: config.model
                })
            })

            if (!response.ok) {
                throw new Error('配置保存失败')
            }

            // 保存到 localStorage
            localStorage.setItem(STORAGE_KEY, JSON.stringify(config))

            setMessage({ type: 'success', text: 'LLM 配置已保存！' })
            setTimeout(() => {
                onClose()
                setMessage(null)
            }, 1500)
        } catch (error) {
            setMessage({ type: 'error', text: '保存失败，请检查网络连接' })
        } finally {
            setSaving(false)
        }
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>LLM API 配置</h2>
                    <button className="close-button" onClick={onClose}>×</button>
                </div>

                <div className="modal-body">
                    <div className="form-group">
                        <label htmlFor="apiKey">API Key *</label>
                        <input
                            id="apiKey"
                            type="password"
                            placeholder="sk-..."
                            value={config.apiKey}
                            onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="baseUrl">Base URL</label>
                        <input
                            id="baseUrl"
                            type="text"
                            placeholder="https://api.openai.com/v1"
                            value={config.baseUrl}
                            onChange={(e) => setConfig({ ...config, baseUrl: e.target.value })}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="model">模型</label>
                        <input
                            id="model"
                            type="text"
                            placeholder="gpt-4o"
                            value={config.model}
                            onChange={(e) => setConfig({ ...config, model: e.target.value })}
                        />
                    </div>

                    {message && (
                        <div className={`message ${message.type}`}>
                            {message.text}
                        </div>
                    )}
                </div>

                <div className="modal-footer">
                    <button className="button secondary" onClick={onClose}>
                        取消
                    </button>
                    <button
                        className="button primary"
                        onClick={handleSave}
                        disabled={saving}
                    >
                        {saving ? '保存中...' : '保存配置'}
                    </button>
                </div>
            </div>
        </div>
    )
}
