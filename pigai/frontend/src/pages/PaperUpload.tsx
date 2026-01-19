import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload } from 'lucide-react';
import api from '../lib/api';
import type { Template } from '../types';

export default function PaperUpload() {
    const navigate = useNavigate();
    const [templates, setTemplates] = useState<Template[]>([]);
    const [selectedTemplate, setSelectedTemplate] = useState<string>('');
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        // Load templates for dropdown
        api.get<Template[]>('/templates/').then(res => setTemplates(res.data));
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file || !selectedTemplate) return;

        setLoading(true);
        const formData = new FormData();
        formData.append('template_id', selectedTemplate);
        formData.append('file', file);

        try {
            await api.post('/papers/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            // Redirect to list or detail (it might be processing)
            navigate('/papers');
        } catch (err) {
            console.error('Failed to upload paper', err);
            alert('Failed to upload paper');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <h1 className="text-2xl font-bold text-gray-800">上传试卷扫描件</h1>

            <div className="bg-white shadow rounded-lg p-6">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">选择试卷模板</label>
                        <select
                            value={selectedTemplate}
                            onChange={(e) => setSelectedTemplate(e.target.value)}
                            required
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                        >
                            <option value="">-- 请选择模板 --</option>
                            {templates.map(t => (
                                <option key={t.id} value={t.id}>{t.name} (ID: {t.id})</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">扫描图片</label>
                        <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                            <div className="space-y-1 text-center">
                                {file ? (
                                    <div className="text-sm text-gray-900">
                                        已选择: {file.name}
                                        <button
                                            type="button"
                                            onClick={() => setFile(null)}
                                            className="ml-2 text-red-600 hover:text-red-500"
                                        >
                                            移除
                                        </button>
                                    </div>
                                ) : (
                                    <>
                                        <Upload className="mx-auto h-12 w-12 text-gray-400" />
                                        <div className="flex text-sm text-gray-600 justify-center">
                                            <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                                                <span>上传图片文件</span>
                                                <input
                                                    type="file"
                                                    className="sr-only"
                                                    accept="image/*"
                                                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                                                    required
                                                />
                                            </label>
                                        </div>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end">
                        <button
                            type="button"
                            onClick={() => navigate('/papers')}
                            className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 mr-3"
                        >
                            取消
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                        >
                            {loading ? '上传处理中...' : '上传并批改'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
