import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Stage, Layer, Image as KonvaImage, Rect, Text, Group } from 'react-konva';
import useImage from 'use-image';
import { ArrowLeft, CheckCircle, XCircle, FileDown } from 'lucide-react';
import api from '../lib/api';
import type { Paper, Template } from '../types';

// URLImage Component
const URLImage = ({ src, onLoaded }: { src: string; onLoaded: (width: number, height: number) => void }) => {
    const [image] = useImage(src);
    useEffect(() => {
        if (image) {
            onLoaded(image.width, image.height);
        }
    }, [image, onLoaded]);
    return <KonvaImage image={image} />;
};

export default function PaperResult() {
    const { id } = useParams<{ id: string }>();
    const [paper, setPaper] = useState<Paper | null>(null);
    const [template, setTemplate] = useState<Template | null>(null);
    const [imageSize, setImageSize] = useState({ width: 800, height: 1000 });

    useEffect(() => {
        if (id) loadData(id);
    }, [id]);

    const loadData = async (paperId: string) => {
        try {
            const paperRes = await api.get<Paper>(`/papers/${paperId}`);
            setPaper(paperRes.data);

            if (paperRes.data.template_id) {
                const tmplRes = await api.get<Template>(`/templates/${paperRes.data.template_id}`);
                setTemplate(tmplRes.data);
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handleDownloadReport = async () => {
        if (!paper) return;
        try {
            const response = await api.get(`/papers/${paper.id}/report`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `report_${paper.id}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error('Failed to download report', err);
            alert('Failed to download report');
        }
    };

    if (!paper || !template) return <div className="p-8">加载中...</div>;

    return (
        <div className="flex h-[calc(100vh-64px)] overflow-hidden">
            {/* Sidebar: Details & Score */}
            <div className="w-80 bg-white border-r flex flex-col p-4 overflow-y-auto">
                <div className="flex items-center mb-6 justify-between">
                    <div className="flex items-center">
                        <Link to="/papers" className="text-gray-600 hover:text-gray-900 mr-2">
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <h2 className="font-bold text-lg">批改详情</h2>
                    </div>
                    <button
                        onClick={handleDownloadReport}
                        className="text-blue-600 hover:text-blue-800"
                        title="下载报告"
                    >
                        <FileDown className="w-5 h-5" />
                    </button>
                </div>

                <div className="mb-6 p-4 bg-blue-50 rounded-lg text-center">
                    <div className="text-sm text-gray-500 uppercase tracking-wide font-semibold">总分</div>
                    <div className="text-4xl font-bold text-blue-600 my-2">{paper.total_score}</div>
                    <div className="text-xs text-gray-400">状态: {
                        paper.status === 'graded' ? '已批改' :
                            paper.status === 'failed' ? '失败' : paper.status
                    }</div>
                </div>

                <div className="space-y-4">
                    <h3 className="font-medium text-gray-700">得分详情</h3>
                    {paper.results.map((res, idx) => (
                        <div key={idx} className={`p-3 rounded border ${res.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                            <div className="flex justify-between items-start">
                                <span className="text-sm font-bold text-gray-700">
                                    题目 {template.regions.find(r => r.id === res.region_id)?.metadata?.question_no || '#'}
                                </span>
                                {res.is_correct ? <CheckCircle className="w-4 h-4 text-green-600" /> : <XCircle className="w-4 h-4 text-red-600" />}
                            </div>
                            <div className="mt-1 text-xs text-gray-600">
                                <strong>识别结果:</strong> {res.ocr_text}
                            </div>
                            {!res.is_correct && (
                                <div className="text-xs text-red-500 mt-1">
                                    {res.feedback}
                                </div>
                            )}
                            <div className="text-right text-xs font-semibold mt-1">
                                得分: {res.score}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Canvas */}
            <div className="flex-1 bg-gray-200 overflow-auto flex justify-center p-8">
                <div className="bg-white shadow-lg fit-content h-fit min-h-[500px] relative">
                    <Stage width={imageSize.width} height={imageSize.height}>
                        <Layer>
                            {/* Show Aligned Image */}
                            <URLImage
                                src={`http://localhost:8000/static/${paper.aligned_image_path || paper.image_path}`}
                                onLoaded={(w, h) => setImageSize({ width: w, height: h })}
                            />

                            {/* Overlay Regions based on Template Regions but colored by Result */}
                            {template.regions.map(region => {
                                const result = paper.results.find(r => r.region_id === region.id);
                                if (!result) return null; // Only show graded regions overlay? Or all?

                                const color = result.is_correct ? 'green' : 'red';

                                return (
                                    <Group key={region.id} x={region.x} y={region.y}>
                                        <Rect
                                            width={region.width}
                                            height={region.height}
                                            stroke={color}
                                            strokeWidth={3}
                                            fill={color}
                                            opacity={0.2}
                                        />
                                        <Text
                                            text={`${result.score}`}
                                            fill={color}
                                            fontSize={20}
                                            fontStyle="bold"
                                            y={-25}
                                        />
                                    </Group>
                                );
                            })}
                        </Layer>
                    </Stage>
                </div>
            </div>
        </div>
    );
}
