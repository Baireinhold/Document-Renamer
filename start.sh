#!/bin/bash
# -*- coding: utf-8 -*-
# 智能文档重命名工具 v2.1 - macOS启动器

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 设置项目目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo
echo "================================================================"
echo -e "${CYAN}             智能文档重命名工具 v2.1${NC}"
echo -e "${CYAN}                 macOS 启动器${NC}"
echo "================================================================"
echo

# 检查Python环境
echo -e "${BLUE}🔍 检查Python环境...${NC}"

PYTHON_CMD=""
for cmd in python3 python3.11 python3.10 python3.9 python3.8 python; do
    if command -v "$cmd" &> /dev/null; then
        VERSION=$($cmd --version 2>&1)
        if [[ $VERSION =~ Python\ 3\.([8-9]|[1-9][0-9]) ]]; then
            PYTHON_CMD="$cmd"
            echo -e "${GREEN}✅ 找到Python: $VERSION (命令: $cmd)${NC}"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    echo -e "${RED}❌ 未找到Python 3.8+${NC}"
    echo
    echo -e "${YELLOW}💡 macOS安装Python建议:${NC}"
    echo "   方法1: 使用Homebrew (推荐)"
    echo "   brew install python3"
    echo
    echo "   方法2: 从官网下载"
    echo "   https://python.org/downloads/macos/"
    echo
    read -p "按回车键退出..."
    exit 1
fi

# 检查pip
echo
echo -e "${BLUE}🔍 检查pip包管理器...${NC}"
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${RED}❌ pip未安装${NC}"
    read -p "按回车键退出..."
    exit 1
fi
echo -e "${GREEN}✅ pip可用${NC}"

# 检查requirements.txt
echo
echo -e "${BLUE}📦 检查依赖文件...${NC}"
if [[ ! -f "requirements.txt" ]]; then
    echo -e "${RED}❌ 未找到requirements.txt文件${NC}"
    read -p "按回车键退出..."
    exit 1
fi
echo -e "${GREEN}✅ requirements.txt文件存在${NC}"

# 检查并安装依赖
echo
echo -e "${BLUE}🔍 检查核心依赖...${NC}"
if ! $PYTHON_CMD -c "import rich, requests, dotenv, yaml, PyPDF2, pdfplumber" &> /dev/null; then
    echo -e "${YELLOW}⚠️  检测到缺失依赖，开始安装...${NC}"
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 依赖安装失败${NC}"
        read -p "按回车键退出..."
        exit 1
    fi
fi
echo -e "${GREEN}✅ 核心依赖已安装${NC}"

# 检查.env文件
echo
echo -e "${BLUE}🔍 检查环境配置文件...${NC}"
if [[ ! -f ".env" ]]; then
    echo -e "${YELLOW}⚠️  未找到.env配置文件，正在创建...${NC}"
    
    # 创建默认.env文件
    cat > .env << 'ENVEOF'
# =====================================
# 智能文档重命名工具 v2.1 - 环境配置
# =====================================

# ====== AI服务配置 (选择一个并取消注释) ======

# OpenAI GPT (全球最强)
# AI_API_KEY=sk-your-openai-api-key
# AI_API_URL=https://api.openai.com/v1/chat/completions
# AI_MODEL=gpt-3.5-turbo

# Claude (逻辑清晰)
# AI_API_KEY=sk-ant-your-claude-api-key
# AI_API_URL=https://api.anthropic.com/v1/messages
# AI_MODEL=claude-3-haiku-20240307

# DeepSeek (推荐，性价比高)
AI_API_KEY=sk-your-deepseek-api-key
AI_API_URL=https://api.deepseek.com/v1/chat/completions
AI_MODEL=deepseek-chat

# ====== 页码控制设置 ======
MIN_PAGES=1
MAX_PAGES=10

# ====== OCR检测设置 ======
OCR_PREFIX=[请OCR]
MIN_TEXT_LENGTH=100

# ====== 处理限制 ======
MAX_FILES_PER_BATCH=50
BATCH_SIZE=5
API_TIMEOUT=30

# ====== 命名模板 ======
BOOK_NAMING_PATTERN={title} - {author} ({year})
PAPER_NAMING_PATTERN={title} - {author} ({year})

# ====== 基本设置 ======
DEFAULT_DOCUMENT_TYPE=book
MIN_CONFIDENCE=0.5
BACKUP_ORIGINAL=true
DRY_RUN=false

# ====== 目录设置 ======
DEFAULT_INPUT_DIR=data/input
DEFAULT_OUTPUT_DIR=data/output
ALLOW_SAME_DIRECTORY=true
ENVEOF

    echo -e "${GREEN}✅ 已创建默认.env配置文件${NC}"
    echo
    echo -e "${YELLOW}📝 重要提醒: 需要配置API密钥${NC}"
    echo "   1. 编辑 .env 文件"
    echo "   2. 设置你的AI API密钥"
    echo "   3. 保存后重新运行"
    echo
    read -p "是否现在打开.env文件编辑? (y/n): " edit_env
    if [[ "$edit_env" =~ ^[Yy]$ ]]; then
        if command -v nano &> /dev/null; then
            nano .env
        elif command -v vim &> /dev/null; then
            vim .env
        else
            open -e .env
        fi
        echo -e "${YELLOW}💡 编辑完成后重新运行此脚本${NC}"
        read -p "按回车键退出..."
        exit 0
    fi
fi
echo -e "${GREEN}✅ .env配置文件存在${NC}"

# 创建必要目录
mkdir -p "data/input" "data/output" "data/logs"

# 启动主程序
echo
echo "================================================================"
echo -e "${CYAN}                     🚀 启动主程序${NC}"
echo "================================================================"
echo

if [[ -f "scripts/run.py" ]]; then
    $PYTHON_CMD scripts/run.py
elif [[ -f "src/main.py" ]]; then
    $PYTHON_CMD src/main.py
else
    echo -e "${RED}❌ 未找到主程序文件${NC}"
    read -p "按回车键退出..."
    exit 1
fi

echo
read -p "按回车键退出..."
