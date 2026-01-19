import os
import json
import logging
from typing import List, Dict, Any
import requests

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        # Default to OpenAI compatible format
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("LLM_MODEL", "gpt-4o")
        
        if not self.api_key:
            logger.warning("LLM_API_KEY not found. LLM Client will run in MOCK mode.")
    
    def update_config(self, api_key: str, base_url: str = None, model: str = None):
        """
        动态更新 LLM 配置
        """
        self.api_key = api_key
        if base_url:
            self.base_url = base_url
        if model:
            self.model = model
        logger.info(f"LLM config updated: base_url={self.base_url}, model={self.model}")

    def grade_text(self, ocr_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Send OCR results to LLM to identify questions, answers, and grade them.
        
        Args:
            ocr_results: List of dicts from OCR service [{'text': '...', 'box': [...]}, ...]
            
        Returns:
            List of graded items:
            [
                {
                    "question_id": 1,
                    "is_correct": True,
                    "confidence": 0.9,
                    "bbox": [[x1,y1], ...], # Bounding box to draw the mark
                    "comment": "Correct answer"
                },
                ...
            ]
        """
        if not self.api_key:
            return self._mock_grade(ocr_results)

        # Construct prompt - provide full OCR data with coordinates
        ocr_data = []
        for i, item in enumerate(ocr_results):
            ocr_data.append({
                "id": i + 1,
                "text": item['text'],
                "box": item['box']
            })
        
        system_prompt = """你是一位专业的试卷批改助手。你的任务是识别试卷上的**答题区域**并判断对错。

**关键理解：**
- 一道题只需要一个判断结果（一个勾或一个叉）
- 不要对每个文字都打标记
- 要识别哪些文字属于同一个答题区域

**识别答题区域的方法：**
1. **选择题**：学生圈选或填写的选项（如 A、B、C、D）算一个答题区域
2. **填空题**：学生填写的内容（可能包含多个文字）算一个答题区域
3. **简答题**：学生手写的答案（可能多行）算一个答题区域

**重要规则：**
- 题目文字、选项标签（A B C D）、题号等**不是答题区域**
- 一道题通常只有一个答题区域
- 如果一道题有多个文字片段，需要合并为一个答题区域

**输出格式（JSON 数组）：**
[
    {
        "question_number": 1,
        "answer_text": "学生填写的答案内容",
        "is_correct": true/false,
        "box": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]  // 答题区域的边界框
    }
]

**示例（4道选择题）：**
输入 OCR 数据：
1. text="1", box=[...]  // 题号
2. text="A", box=[[100,200], [120,200], [120,220], [100,220]]  // 学生选择的答案
3. text="B", box=[...]  // 其他选项
4. text="C", box=[...]  // 其他选项
5. text="2", box=[...]  // 题号
6. text="A", box=[...]  // 选项
7. text="B", box=[[100,300], [120,300], [120,320], [100,320]]  // 学生选择的答案
...

正确输出（只返回4个判断）：
[
    {"question_number": 1, "answer_text": "A", "is_correct": true, "box": [[100,200], [120,200], [120,220], [100,220]]},
    {"question_number": 2, "answer_text": "B", "is_correct": false, "box": [[100,300], [120,300], [120,320], [100,320]]},
    {"question_number": 3, "answer_text": "C", "is_correct": true, "box": [...]},
    {"question_number": 4, "answer_text": "D", "is_correct": false, "box": [...]}
]

**注意：**
- 返回的数量应该等于题目数量，不是 OCR 文字数量
- 返回的数量应该等于题目数量，不是 OCR 文字数量
- 每个答题区域只返回一次
- 如果试卷有4道题，就返回4个结果
"""

        user_prompt = f"""以下是从试卷中提取的 OCR 文字及其坐标：

{json.dumps(ocr_data, ensure_ascii=False, indent=2)}

请识别出**答题区域**（不是每个文字），每道题返回一个判断结果。

要求：
1. 识别出学生填写的答案区域
2. 过滤掉题目、题号、选项标签等
3. 合并属于同一道题的多个文字片段
4. 返回的数量应该接近题目数量

请只返回 JSON 数组。"""

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 3000
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Handle DeepSeek-R1 reasoning content
            message = result["choices"][0]["message"]
            content = message.get("content", "")
            
            if not content and "reasoning_content" in message:
                logger.info("Using reasoning_content from DeepSeek-R1")
                content = message["reasoning_content"]
            
            logger.info(f"LLM response length: {len(content)} chars")
            logger.info(f"LLM response preview: {content[:300]}...")
            
            # Parse JSON
            parsed_data = json.loads(content)
            
            # Handle different response formats
            graded_items = []
            if isinstance(parsed_data, dict):
                for key in ["data", "results", "answers", "items", "questions"]:
                    if key in parsed_data and isinstance(parsed_data[key], list):
                        graded_items = parsed_data[key]
                        break
                if not graded_items:
                    graded_items = [parsed_data]
            elif isinstance(parsed_data, list):
                graded_items = parsed_data
            
            # Convert to expected format
            formatted_results = []
            for item in graded_items:
                # Handle different field names
                text_content = item.get("answer_text") or item.get("text_content") or item.get("text", "")
                is_correct = item.get("is_correct", False)
                box = item.get("box", [])
                
                if text_content and box:
                    formatted_results.append({
                        "text_content": text_content,
                        "is_correct": is_correct,
                        "box": box
                    })
            
            logger.info(f"LLM returned {len(graded_items)} answer regions")
            return formatted_results
            
        except Exception as e:
            logger.error(f"LLM Grading failed: {e}")
            return self._mock_grade(ocr_results)

    def _mock_grade(self, ocr_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mock grader for testing without API key. 
        Filters and randomly grades text that looks like student answers.
        """
        import random
        graded = []
        logger.info(f"Mock grading {len(ocr_results)} OCR results")
        
        for i, item in enumerate(ocr_results):
            text = item.get('text', '')
            box = item.get('box', [])
            
            # Debug: log the first item to see structure
            if i == 0:
                logger.info(f"First OCR item: text='{text}', box={box}, box_type={type(box)}")
            
            # Filter: Only grade text that looks like answers
            # Skip if text is too long (likely a question or instruction)
            if len(text) > 20:
                continue
            
            # Skip common non-answer patterns
            skip_patterns = ['题', '答案', '姓名', '班级', '学号', '分数', '选择', '填空', '判断']
            if any(pattern in text for pattern in skip_patterns):
                continue
            
            # Skip if text is just numbers (likely question numbers)
            if text.isdigit() and len(text) <= 2:
                continue
            
            # Grade remaining text (likely answers)
            graded.append({
                "text_content": text,
                "is_correct": random.choice([True, False]),
                "box": box  # Pass the box coordinates directly
            })
            
        logger.info(f"Mock grading generated {len(graded)} marks (filtered from {len(ocr_results)} total)")
        if len(graded) > 0:
            logger.info(f"First graded item: {graded[0]}")
        return graded

llm_client = LLMClient()
