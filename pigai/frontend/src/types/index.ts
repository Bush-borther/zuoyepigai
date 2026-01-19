export interface Region {
    id: string;
    x: number;
    y: number;
    width: number;
    height: number;
    type: 'question_id' | 'score_box' | 'answer_area';
    metadata?: any;
}

export interface Template {
    id: number;
    name: string;
    image_path: string;
    width: number;
    height: number;
    regions: Region[];
    created_at: string;
}

export interface GradingResult {
    region_id: string;
    ocr_text: string;
    is_correct: boolean;
    score: number;
    feedback: string;
}

export interface Paper {
    id: number;
    template_id: number;
    image_path: string;
    aligned_image_path?: string;
    status: string;
    total_score: number;
    results: GradingResult[];
    created_at: string;
}
