import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Eye } from 'lucide-react';
import api from '../lib/api';
import type { Paper } from '../types';

export default function PaperList() {
    const [papers, setPapers] = useState<Paper[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadPapers();
    }, []);

    const loadPapers = async () => {
        try {
            const res = await api.get<Paper[]>('/papers/');
            setPapers(res.data);
        } catch (err) {
            console.error('Failed to load papers', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8">Loading...</div>;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-800">试卷批改</h1>
                <Link
                    to="/papers/upload"
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                    <Plus className="w-5 h-5 mr-2" />
                    上传试卷
                </Link>
            </div>

            <div className="bg-white shadow rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">模板 ID</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">得分</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">上传时间</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {papers.map((paper) => (
                            <tr key={paper.id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">#{paper.id}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">#{paper.template_id}</td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${paper.status === 'graded' ? 'bg-green-100 text-green-800' :
                                        paper.status === 'failed' ? 'bg-red-100 text-red-800' :
                                            'bg-yellow-100 text-yellow-800'
                                        }`}>
                                        {paper.status === 'graded' ? '已批改' :
                                            paper.status === 'failed' ? '失败' :
                                                paper.status === 'pending' ? '等待中' :
                                                    paper.status === 'grading_queued' ? '批改中' : paper.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-bold">
                                    {paper.total_score}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {new Date(paper.created_at).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                    {paper.status === 'graded' || paper.status === 'grading_queued' ? (
                                        <Link
                                            to={`/papers/${paper.id}`}
                                            className="text-blue-600 hover:text-blue-900"
                                        >
                                            <Eye className="w-5 h-5 inline mr-1" />
                                            查看结果
                                        </Link>
                                    ) : (
                                        <span className="text-gray-400">处理中...</span>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {papers.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                        暂无批改记录，请点击右上角上传试卷。
                    </div>
                )}
            </div>
        </div>
    );
}
