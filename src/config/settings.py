#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版配置管理器 - 支持完整自定义选项
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

class ConfigManager:
    """增强版配置管理器"""
    
    def __init__(self):
        # 获取项目根目录
        if hasattr(sys, '_MEIPASS'):
            self.project_root = Path(sys._MEIPASS)
        else:
            self.project_root = Path(__file__).parent.parent.parent
        
        self.env_path = self.project_root / ".env"
        
        # 加载环境变量
        if self.env_path.exists():
            load_dotenv(self.env_path)
        
        # 构建配置
        self.config = self.build_config()
    
    def build_config(self):
        """构建完整配置字典"""
        return {
            # AI服务配置
            "ai_service": {
                "api_key": os.getenv("AI_API_KEY", ""),
                "api_url": os.getenv("AI_API_URL", "https://api.deepseek.com/v1/chat/completions"),
                "model": os.getenv("AI_MODEL", "deepseek-chat"),
                "timeout": int(os.getenv("API_TIMEOUT", "30")),
                "max_retries": int(os.getenv("MAX_RETRIES", "3")),
                "retry_delay": int(os.getenv("RETRY_DELAY", "2"))
            },
            
            # 文本提取配置
            "text_extraction": {
                "min_pages": int(os.getenv("MIN_PAGES", "1")),
                "max_pages": int(os.getenv("MAX_PAGES", "10")),
                "min_text_length": int(os.getenv("MIN_TEXT_LENGTH", "100"))
            },
            
            # OCR检测配置
            "ocr_detection": {
                "enabled": os.getenv("AUTO_OCR_DETECTION", "true").lower() == "true",
                "prefix": os.getenv("OCR_PREFIX", "[请OCR]"),
                "min_text_length": int(os.getenv("MIN_TEXT_LENGTH", "100"))
            },
            
            # 处理配置
            "processing": {
                "max_files_per_batch": int(os.getenv("MAX_FILES_PER_BATCH", "50")),
                "batch_size": int(os.getenv("BATCH_SIZE", "5")),
                "concurrent_workers": int(os.getenv("CONCURRENT_WORKERS", "2")),
                "batch_delay": int(os.getenv("BATCH_DELAY", "1")),
                "min_confidence": float(os.getenv("MIN_CONFIDENCE", "0.5")),
                "dry_run": os.getenv("DRY_RUN", "false").lower() == "true",
                "backup_original": os.getenv("BACKUP_ORIGINAL", "true").lower() == "true"
            },
            
            # 书籍命名配置
            "book_processing": {
                "naming_pattern": os.getenv("BOOK_NAMING_PATTERN", "{title} - {author} ({year})"),
                "extract_fields": {
                    "title": True,      # 书名
                    "author": True,     # 作者
                    "publisher": True,  # 出版社
                    "year": True        # 出版时间
                },
                "translation": {
                    "enabled": os.getenv("ENABLE_TRANSLATION", "false").lower() == "true",
                    "target_language": os.getenv("TRANSLATION_TARGET", "zh"),
                    "translate_title": os.getenv("TRANSLATE_BOOK_TITLE", "false").lower() == "true",
                    "translate_author": os.getenv("TRANSLATE_BOOK_AUTHOR", "false").lower() == "true",
                    "translate_publisher": os.getenv("TRANSLATE_BOOK_PUBLISHER", "false").lower() == "true",
                    "keep_original": os.getenv("KEEP_ORIGINAL_TEXT", "true").lower() == "true"
                }
            },
            
            # 论文命名配置
            "paper_processing": {
                "naming_pattern": os.getenv("PAPER_NAMING_PATTERN", "{title} - {author} ({year})"),
                "extract_fields": {
                    "title": True,    # 文章名
                    "author": True,   # 作者
                    "journal": True,  # 期刊名
                    "year": True      # 出版时间
                },
                "translation": {
                    "enabled": os.getenv("ENABLE_TRANSLATION", "false").lower() == "true",
                    "target_language": os.getenv("TRANSLATION_TARGET", "zh"),
                    "translate_title": os.getenv("TRANSLATE_PAPER_TITLE", "false").lower() == "true",
                    "translate_author": os.getenv("TRANSLATE_PAPER_AUTHOR", "false").lower() == "true",
                    "translate_journal": os.getenv("TRANSLATE_PAPER_JOURNAL", "false").lower() == "true",
                    "keep_original": os.getenv("KEEP_ORIGINAL_TEXT", "true").lower() == "true"
                }
            },
            
            # 文件命名配置
            "file_naming": {
                "max_filename_length": int(os.getenv("MAX_FILENAME_LENGTH", "200")),
                "ocr_prefix": os.getenv("OCR_PREFIX", "[请OCR]"),
                "book_pattern": os.getenv("BOOK_NAMING_PATTERN", "{title} - {author} ({year})"),  # 注意这里
                "paper_pattern": os.getenv("PAPER_NAMING_PATTERN", "{title} - {author} ({year})"), # 注意这里
                "illegal_char_replacement": os.getenv("ILLEGAL_CHAR_REPLACEMENT", "_"),
                "clean_filename": os.getenv("CLEAN_FILENAME", "true").lower() == "true"
            },
            # 目录配置
            "directories": {
                "default_input": os.getenv("DEFAULT_INPUT_DIR", "data/input"),
                "default_output": os.getenv("DEFAULT_OUTPUT_DIR", "data/output"),
                "allow_same_directory": os.getenv("ALLOW_SAME_DIRECTORY", "true").lower() == "true"
            },
            
            # 文档类型检测
            "document_detection": {
                "enabled": os.getenv("AUTO_DETECT_TYPE", "true").lower() == "true",
                "default_type": os.getenv("DEFAULT_DOCUMENT_TYPE", "book"),
                "book_keywords": ["出版社", "ISBN", "版权", "publisher", "copyright", "edition", "press"],
                "paper_keywords": ["期刊", "journal", "conference", "proceedings", "doi", "abstract", "volume", "issue"]
            },
            
            # 界面配置
            "ui": {
                "language": os.getenv("UI_LANGUAGE", "zh"),
                "show_debug": os.getenv("SHOW_DEBUG", "false").lower() == "true",
                "auto_confirm": os.getenv("AUTO_CONFIRM", "false").lower() == "true",
                "show_progress": os.getenv("SHOW_PROGRESS", "true").lower() == "true"
            },
            
            # 日志配置
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "to_file": os.getenv("LOG_TO_FILE", "true").lower() == "true",
                "to_console": os.getenv("LOG_TO_CONSOLE", "true").lower() == "true",
                "max_size_mb": int(os.getenv("MAX_LOG_SIZE", "50")),
                "backup_count": int(os.getenv("LOG_BACKUP_COUNT", "5"))
            }
        }
    
    def validate_config(self):
        """验证配置"""
        api_key = self.config['ai_service']['api_key']
        
        # 检查API密钥
        invalid_keys = [
            "sk-your-deepseek-api-key", "sk-your-openai-api-key",
            "sk-ant-your-claude-api-key", "your-google-api-key",
            "your-zhipu-api-key", "sk-your-moonshot-api-key",
            "your-baidu-api-key", ""
        ]
        
        if not api_key or api_key in invalid_keys:
            return False, "未设置有效的AI API密钥"
        
        # 验证页码设置
        min_pages = self.config['text_extraction']['min_pages']
        max_pages = self.config['text_extraction']['max_pages']
        
        if min_pages < 1:
            return False, "最小页码不能小于1"
        
        if max_pages < min_pages:
            return False, "最大页码不能小于最小页码"
        
        # 验证命名模板
        book_pattern = self.config['book_processing']['naming_pattern']
        paper_pattern = self.config['paper_processing']['naming_pattern']
        
        if not book_pattern.strip():
            return False, "书籍命名模板不能为空"
        
        if not paper_pattern.strip():
            return False, "论文命名模板不能为空"
        
        # 测试API连接（可选）
        try:
            return self.test_api_connection()
        except Exception as e:
            return False, f"配置验证异常: {str(e)}"
    
    def test_api_connection(self):
        """测试API连接"""
        try:
            api_config = self.config['ai_service']
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_config['api_key']}"
            }
            
            test_data = {
                "model": api_config['model'],
                "messages": [{"role": "user", "content": "测试"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                api_config['api_url'],
                headers=headers,
                json=test_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "配置验证通过，API连接正常"
            elif response.status_code == 401:
                return False, "API密钥无效"
            elif response.status_code == 429:
                return True, "API密钥有效（触发速率限制）"
            else:
                return False, f"API连接失败，状态码: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "API连接超时"
        except requests.exceptions.ConnectionError:
            return False, "无法连接到API服务器"
        except Exception as e:
            return False, f"API连接测试失败: {str(e)}"
    
    def get_naming_pattern_variables(self, doc_type):
        """获取命名模板可用变量"""
        if doc_type == "book":
            return {
                "title": "书名",
                "author": "作者",
                "publisher": "出版社", 
                "year": "出版年份"
            }
        else:  # paper
            return {
                "title": "文章标题",
                "author": "作者",
                "journal": "期刊名",
                "year": "发表年份"
            }
    
    def validate_naming_pattern(self, pattern, doc_type):
        """验证命名模板"""
        try:
            available_vars = self.get_naming_pattern_variables(doc_type)
            
            # 尝试格式化模板
            test_values = {key: f"测试{desc}" for key, desc in available_vars.items()}
            pattern.format(**test_values)
            
            return True, "命名模板格式正确"
        except KeyError as e:
            return False, f"命名模板包含无效变量: {e}"
        except Exception as e:
            return False, f"命名模板格式错误: {e}"
    
    def show_config_summary(self):
        """显示配置摘要"""
        summary = f"""
配置摘要:
- AI服务: {self.config['ai_service']['model']}
- 页码范围: {self.config['text_extraction']['min_pages']}-{self.config['text_extraction']['max_pages']}
- 书籍命名: {self.config['book_processing']['naming_pattern']}
- 论文命名: {self.config['paper_processing']['naming_pattern']}
- 翻译功能: {'启用' if self.config['book_processing']['translation']['enabled'] else '禁用'}
- OCR检测: {'启用' if self.config['ocr_detection']['enabled'] else '禁用'}
- 模拟运行: {'是' if self.config['processing']['dry_run'] else '否'}
        """
        return summary.strip()