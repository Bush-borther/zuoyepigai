import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Stage, Layer, Image as KonvaImage, Rect, Text, Group } from 'react-konva';
import useImage from 'use-image';
import { Save, ArrowLeft, Trash2, MousePointer, PlusSquare } from 'lucide-react';
import api from '../lib/api';
import type { Template, Region } from '../types';

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

export default function TemplateEditor() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [template, setTemplate] = useState<Template | null>(null);
    const [regions, setRegions] = useState<Region[]>([]);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [mode, setMode] = useState<'select' | 'draw'>('select');
    const [saving, setSaving] = useState(false);

    // Drawing state
    const isDrawing = useRef(false);
    const startPos = useRef({ x: 0, y: 0 });
    const [newRegion, setNewRegion] = useState<{ x: number, y: number, width: number, height: number } | null>(null);

    useEffect(() => {
        if (id) loadTemplate(id);
    }, [id]);

    const loadTemplate = async (templateId: string) => {
        try {
            const res = await api.get<Template>(`/templates/${templateId}`);
            setTemplate(res.data);
            setRegions(res.data.regions || []);
        } catch (err) {
            console.error('Failed to load template', err);
        }
    };

    const handleSave = async () => {
        if (!template) return;
        setSaving(true);
        try {
            await api.put(`/templates/${template.id}`, {
                regions: regions
            });
            alert('模板保存成功！');
        } catch (err) {
            console.error('Failed to save', err);
            alert('保存模板失败');
        } finally {
            setSaving(false);
        }
    };

    const handleMouseDown = (e: any) => {
        if (mode !== 'draw') {
            const clickedOnEmpty = e.target === e.target.getStage();
            if (clickedOnEmpty) {
                setSelectedId(null);
            }
            return;
        }

        isDrawing.current = true;
        const stage = e.target.getStage();
        const pos = stage.getPointerPosition();
        startPos.current = { x: pos.x, y: pos.y };
        setNewRegion({ x: pos.x, y: pos.y, width: 0, height: 0 });
    };

    const handleMouseMove = (e: any) => {
        if (!isDrawing.current || mode !== 'draw') return;

        const stage = e.target.getStage();
        const pos = stage.getPointerPosition();
        const x = startPos.current.x;
        const y = startPos.current.y;

        setNewRegion({
            x: Math.min(x, pos.x),
            y: Math.min(y, pos.y),
            width: Math.abs(pos.x - x),
            height: Math.abs(pos.y - y),
        });
    };

    const handleMouseUp = () => {
        if (!isDrawing.current || mode !== 'draw' || !newRegion) return;
        isDrawing.current = false;

        // Add new region if big enough
        if (newRegion.width > 5 && newRegion.height > 5) {
            const id = crypto.randomUUID();
            const region: Region = {
                id,
                ...newRegion,
                type: 'answer_area' // default
            };
            setRegions([...regions, region]);
            setSelectedId(id);
            setMode('select'); // Switch back to select after draw
        }
        setNewRegion(null);
    };

    const handleRegionChange = (id: string, newAttrs: Partial<Region>) => {
        setRegions(regions.map(r => r.id === id ? { ...r, ...newAttrs } : r));
    };

    // New function for deleting region
    const deleteRegion = (idToDelete: string) => {
        setRegions(regions.filter(r => r.id !== idToDelete));
        setSelectedId(null);
    };

    const selectedRegion = regions.find(r => r.id === selectedId);

    return (
        <div className="flex h-[calc(100vh-64px)] overflow-hidden">
            {/* Sidebar: Properties */}
            <div className="w-80 bg-white border-r flex flex-col">
                <div className="p-4 border-b flex justify-between items-center bg-gray-50">
                    <div className="flex items-center">
                        <Link to="/templates" className="text-gray-600 hover:text-gray-900 mr-2">
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <h2 className="font-bold text-gray-800">模板编辑器</h2>
                    </div>
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                        title="保存模板"
                    >
                        <Save className="w-5 h-5" />
                    </button>
                </div>

                <div className="p-4 flex-1 overflow-y-auto space-y-6">
                    {/* Toolbar */}
                    <div>
                        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">工具栏</h3>
                        <div className="flex space-x-2">
                            <button
                                onClick={() => setIsDrawingMode(true)}
                                className={`flex items-center px-3 py-2 rounded text-sm font-medium ${isDrawingMode ? 'bg-blue-100 text-blue-700' : 'bg-white border text-gray-700 hover:bg-gray-50'}`}
                            >
                                <PlusSquare className="w-4 h-4 mr-2" />
                                绘制选区
                            </button>
                            <button
                                onClick={() => setIsDrawingMode(false)}
                                className={`flex items-center px-3 py-2 rounded text-sm font-medium ${!isDrawingMode ? 'bg-blue-100 text-blue-700' : 'bg-white border text-gray-700 hover:bg-gray-50'}`}
                            >
                                <MousePointer className="w-4 h-4 mr-2" />
                                选择模式
                            </button>
                        </div>
                        {isDrawingMode && <p className="text-xs text-blue-600 mt-2">在图片上拖动鼠标创建答题区域</p>}
                    </div>

                    {/* Selected Region Properties */}
                    {selectedRegion ? (
                        <div className="border-t pt-4">
                            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">区域属性</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700">类型</label>
                                    <select
                                        value={selectedRegion.type}
                                        onChange={(e) => updateRegion(selectedRegion.id, { type: e.target.value as any })}
                                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                                    >
                                        <option value="question_id">题号</option>
                                        <option value="answer_area">答题区域</option>
                                        <option value="score_box">得分框</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700">区域 I D</label>
                                    <input
                                        type="text"
                                        value={selectedRegion.id}
                                        disabled
                                        className="mt-1 block w-full rounded-md border-gray-300 bg-gray-100 sm:text-sm p-2 border"
                                    />
                                </div>

                                {selectedRegion.type === 'question_id' && (
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700">题号文本</label>
                                        <input
                                            type="text"
                                            value={selectedRegion.metadata?.question_no || ''}
                                            onChange={(e) => updateRegion(selectedRegion.id, { metadata: { ...selectedRegion.metadata, question_no: e.target.value } })}
                                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                                            placeholder="例如: 1"
                                        />
                                    </div>
                                )}

                                {selectedRegion.type === 'answer_area' && (
                                    <>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700">标准答案</label>
                                            <input
                                                type="text"
                                                value={selectedRegion.metadata?.answer || ''}
                                                onChange={(e) => updateRegion(selectedRegion.id, { metadata: { ...selectedRegion.metadata, answer: e.target.value } })}
                                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                                                placeholder="输入正确答案"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700">分数</label>
                                            <input
                                                type="number"
                                                value={selectedRegion.metadata?.max_score || ''}
                                                onChange={(e) => updateRegion(selectedRegion.id, { metadata: { ...selectedRegion.metadata, max_score: parseFloat(e.target.value) } })}
                                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
                                            />
                                        </div>
                                    </>
                                )}

                                <div className="pt-2">
                                    <button
                                        onClick={() => deleteRegion(selectedRegion.id)}
                                        className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none"
                                    >
                                        <Trash2 className="w-4 h-4 mr-2" />
                                        删除区域
                                    </button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="border-t pt-4 text-center text-gray-500 text-sm">
                            <p>在左侧图片中选择一个区域进行编辑</p>
                        </div>
                    )}

                    {/* Region List */}
                    <div className="border-t pt-4">
                        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">区域列表 ({regions.length})</h3>
                        <ul className="space-y-2">
                            {regions.map(r => (
                                <li
                                    key={r.id}
                                    onClick={() => setSelectedId(r.id)}
                                    className={`text-xs p-2 rounded cursor-pointer flex justify-between items-center ${selectedId === r.id ? 'bg-blue-50 border border-blue-200' : 'bg-gray-50 hover:bg-gray-100'}`}
                                >
                                    <span>{r.metadata?.question_no || '无题号'}</span> {/* Localized */}
                                    <span className="text-gray-400">
                                        {r.type === 'question_id' ? '题号' : r.type === 'answer_area' ? '答题区域' : '得分框'} {/* Localized */}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>

            {/* Canvas Area */}
            <div className="flex-1 bg-gray-200 overflow-auto flex justify-center p-8">
                <div className="bg-white shadow-lg fit-content h-fit min-h-[500px] relative">
                    {!template ? (
                        <div className="flex items-center justify-center w-full h-full text-gray-400 p-20">加载中...</div>
                    ) : (
                        <Stage
                            width={template.width || 800}
                            height={template.height || 1000}
                            onMouseDown={handleMouseDown}
                            onMouseMove={handleMouseMove}
                            onMouseUp={handleMouseUp}
                        >
                            <Layer>
                                <URLImage
                                    src={`http://localhost:8000/static/${template.image_path}`}
                                    onLoaded={(w, h) => console.log('Image loaded', w, h)}
                                />
                                {regions.map((region) => {
                                    const isSelected = region.id === selectedId;
                                    const color = region.type === 'question_id' ? '#3b82f6' : region.type === 'score_box' ? '#ef4444' : '#10b981';

                                    return (
                                        <Group key={region.id} draggable={mode === 'select'}
                                            x={region.x} y={region.y}
                                            onDragEnd={(e) => {
                                                handleRegionChange(region.id, {
                                                    x: e.target.x(),
                                                    y: e.target.y()
                                                });
                                            }}
                                            onClick={(e) => {
                                                e.cancelBubble = true;
                                                setSelectedId(region.id);
                                            }}
                                        >
                                            <Rect
                                                width={region.width}
                                                height={region.height}
                                                fill={color}
                                                opacity={0.3}
                                                stroke={isSelected ? 'blue' : color}
                                                strokeWidth={isSelected ? 2 : 1}
                                            />
                                            {isSelected && mode === 'select' && (
                                                <Rect
                                                    // Mock transformer visual or just use stroke
                                                    width={region.width}
                                                    height={region.height}
                                                    stroke="blue"
                                                    strokeWidth={2}
                                                />
                                            )}
                                            <Text
                                                text={region.metadata?.question_no || '#'}
                                                fill="black"
                                                fontSize={14}
                                                y={-18}
                                                fontStyle='bold'
                                            />
                                        </Group>
                                    );
                                })}

                                {newRegion && (
                                    <Rect
                                        x={newRegion.x}
                                        y={newRegion.y}
                                        width={newRegion.width}
                                        height={newRegion.height}
                                        stroke="blue"
                                        strokeWidth={1}
                                        dash={[5, 5]}
                                    />
                                )}
                            </Layer>
                        </Stage>
                    )}
                </div>
            </div>
        </div>
    );
}
