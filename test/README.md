# Smart Exam Grading System
# 智能试卷批改系统

[English](#english) | [中文](#chinese)

---

## English

### Overview

An intelligent exam grading system that uses OCR and LLM to automatically grade handwritten test papers and generate marked PDFs.

### Features

- 📝 **OCR Recognition**: Extracts text from scanned exam papers using PaddleOCR
- 🤖 **AI Grading**: Uses LLM to intelligently grade answers
- ✅ **Visual Feedback**: Marks correct answers with ✓ and incorrect ones with ✗
- 📄 **PDF Generation**: Creates downloadable graded PDFs
- 🎯 **Spatial Segmentation**: Automatically detects question regions
- ⚙️ **Flexible Configuration**: Supports multiple LLM providers (OpenAI, DeepSeek, NVIDIA, etc.)

### Tech Stack

**Backend:**
- FastAPI
- PaddleOCR
- Pillow (Image Processing)
- Python 3.10+

**Frontend:**
- React + TypeScript
- Vite
- Modern CSS

### Installation

#### Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- npm or yarn

#### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p backend/static/uploads backend/static/results
```

#### Frontend Setup

```bash
cd frontend
npm install
```

#### Environment Configuration (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your LLM API key
# If not configured, the system runs in MOCK mode
```

### Usage

#### Start Backend

```bash
# From project root
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Start Frontend

```bash
cd frontend
npm run dev -- --host
```

#### Access Application

Open your browser and navigate to: `http://localhost:5173`

### Configuration

#### LLM API Configuration

You can configure LLM API in two ways:

1. **Environment Variables** (`.env` file):
```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
```

2. **Web Interface**: Click the settings icon (⚙️) in the top-right corner

#### Supported LLM Providers

- OpenAI (GPT-4, GPT-3.5)
- DeepSeek
- NVIDIA NIM
- Any OpenAI-compatible API

### Project Structure

```
.
├── backend/
│   ├── api/              # API endpoints
│   ├── service/          # Business logic
│   │   ├── ocr_service.py       # OCR processing
│   │   ├── llm_client.py        # LLM integration
│   │   ├── grading_service.py   # Grading logic
│   │   └── image_processor.py   # Image marking
│   ├── static/           # Static files
│   └── main.py           # Application entry
├── frontend/
│   └── src/
│       ├── components/   # React components
│       └── App.tsx       # Main application
└── README.md
```

### How It Works

1. **Upload**: User uploads a scanned exam paper image
2. **OCR**: PaddleOCR extracts all text and coordinates
3. **Segmentation**: System detects question regions by finding question numbers (1, 2, 3...)
4. **Grading**: Each region is sent to LLM for grading
5. **Marking**: Draws ✓ or ✗ marks on the image
6. **PDF**: Generates a downloadable PDF with marks

### License

MIT

---

## Chinese

### 概述

一个智能试卷批改系统，使用 OCR 和大语言模型自动批改手写试卷并生成标注 PDF。

### 功能特性

- 📝 **OCR 识别**：使用 PaddleOCR 从扫描试卷中提取文字
- 🤖 **AI 判题**：使用大语言模型智能判断答案对错
- ✅ **视觉反馈**：在正确答案上打 ✓，错误答案上打 ✗
- 📄 **PDF 生成**：创建可下载的批改后 PDF
- 🎯 **空间分割**：自动检测题目区域
- ⚙️ **灵活配置**：支持多种 LLM 提供商（OpenAI、DeepSeek、NVIDIA 等）

### 技术栈

**后端：**
- FastAPI
- PaddleOCR
- Pillow（图像处理）
- Python 3.10+

**前端：**
- React + TypeScript
- Vite
- 现代 CSS

### 安装

#### 环境要求

- Python 3.10 或更高版本
- Node.js 16 或更高版本
- npm 或 yarn

#### 后端设置

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 创建必要的目录
mkdir -p backend/static/uploads backend/static/results
```

#### 前端设置

```bash
cd frontend
npm install
```

#### 环境配置（可选）

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 并添加您的 LLM API 密钥
# 如果不配置，系统将以 MOCK 模式运行
```

### 使用方法

#### 启动后端

```bash
# 在项目根目录
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 启动前端

```bash
cd frontend
npm run dev -- --host
```

#### 访问应用

在浏览器中打开：`http://localhost:5173`

### 配置说明

#### LLM API 配置

可以通过两种方式配置 LLM API：

1. **环境变量**（`.env` 文件）：
```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
```

2. **网页界面**：点击右上角的设置图标（⚙️）

#### 支持的 LLM 提供商

- OpenAI（GPT-4、GPT-3.5）
- DeepSeek
- NVIDIA NIM
- 任何兼容 OpenAI API 的服务

### 项目结构

```
.
├── backend/
│   ├── api/              # API 端点
│   ├── service/          # 业务逻辑
│   │   ├── ocr_service.py       # OCR 处理
│   │   ├── llm_client.py        # LLM 集成
│   │   ├── grading_service.py   # 判题逻辑
│   │   └── image_processor.py   # 图像标注
│   ├── static/           # 静态文件
│   └── main.py           # 应用入口
├── frontend/
│   └── src/
│       ├── components/   # React 组件
│       └── App.tsx       # 主应用
└── README.md
```

### 工作原理

1. **上传**：用户上传扫描的试卷图片
2. **OCR**：PaddleOCR 提取所有文字和坐标
3. **分割**：系统通过检测题号（1、2、3...）来识别题目区域
4. **判题**：每个区域发送给 LLM 进行判题
5. **标注**：在图片上绘制 ✓ 或 ✗ 标记
6. **PDF**：生成可下载的带标记 PDF

### 许可证

MIT
