#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文档重命名工具 v2.1 - 主程序
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Tuple
import re
import json
import shutil

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    import requests
    import PyPDF2
    import pdfplumber
except ImportError as e:
    print(f"❌ 导入依赖失败: {e}")
    print("💡 请运行: pip install -r requirements.txt")
    input("按回车键退出...")
    sys.exit(1)

from src.config.settings import ConfigManager
from src.utils.logger import setup_logger

__version__ = "2.1.0"
console = Console()

class DocumentRenamer:
    """智能文档重命名器"""
    
    def __init__(self):
        """初始化"""
        self.version = __version__
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        self.logger = setup_logger()
        
        # 统计信息
        self.stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "books": 0,
            "papers": 0,
            "ocr_needed": 0
        }
        
        self.show_welcome()
    
    def show_welcome(self):
        """显示欢迎信息"""
        welcome_text = f"""
    📚 智能文档重命名工具 v{self.version}
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    👨‍💻 作者：Baireinhold  |  🌟 开源项目  |  📧 技术支持

    ✨ 核心功能:
    • 🔍 真实AI分析（非模拟）
    • 📄 OCR检测和提示  
    • 📊 页码范围控制（{self.config['text_extraction']['min_pages']}-{self.config['text_extraction']['max_pages']}页）
    • 🌍 多AI服务支持
    • 📁 自定义输入输出目录
    • 🔄 原地重命名选项
    • 📝 批量处理限制（最多{self.config['processing']['max_files_per_batch']}个文件）

    🤖 当前AI服务: {self.config['ai_service']['model']}
        """
        
        panel = Panel.fit(welcome_text, style="bold blue", title="欢迎使用")
        console.print(panel)
    
    def get_user_settings(self):
        """获取用户自定义设置"""
        console.print("\n[yellow]🔧 自定义设置（按回车使用默认值）:")
        
        # 页码范围设置
        current_min = self.config['text_extraction']['min_pages']
        current_max = self.config['text_extraction']['max_pages']
        
        console.print(f"\n📄 当前页码范围: {current_min}-{current_max}页")
        
        try:
            min_pages = IntPrompt.ask("请输入最小页码", default=current_min)
            max_pages = IntPrompt.ask("请输入最大页码", default=current_max)
            
            if min_pages > max_pages:
                min_pages, max_pages = max_pages, min_pages
                console.print("[yellow]⚠️ 已自动调整页码顺序")
            
            console.print(f"[green]✅ 页码范围设置为: {min_pages}-{max_pages}页")
            
        except:
            min_pages, max_pages = current_min, current_max
        
        # 目录设置
        console.print(f"\n📁 目录设置:")
        
        default_input = self.config['directories']['default_input']
        default_output = self.config['directories']['default_output']
        
        input_dir = Prompt.ask("请输入PDF输入目录", default=default_input)
        output_dir = Prompt.ask("请输入重命名结果输出目录", default=default_output)
        
        # 检查是否为同一目录
        input_path = Path(input_dir).resolve()
        output_path = Path(output_dir).resolve()
        same_directory = input_path == output_path
        
        if same_directory:
            console.print("[yellow]⚠️ 输入输出目录相同，将直接重命名原文件")
            if not Confirm.ask("确定要直接修改原文件名吗？"):
                output_dir = Prompt.ask("请重新输入输出目录", default=default_output)
                same_directory = False
        
        return {
            'input_dir': input_dir,
            'output_dir': output_dir,
            'min_pages': min_pages,
            'max_pages': max_pages,
            'same_directory': same_directory
        }
    
    def extract_pdf_text(self, file_path: Path, min_pages: int, max_pages: int) -> Tuple[str, str]:
        """提取PDF文本"""
        text = ""
        method = "unknown"
        
        try:
            # 方法1: 使用pdfplumber
            try:
                with pdfplumber.open(file_path) as pdf:
                    total_pages = len(pdf.pages)
                    start_page = max(0, min_pages - 1)
                    end_page = min(total_pages, max_pages)
                    
                    page_texts = []
                    for i in range(start_page, end_page):
                        page = pdf.pages[i]
                        page_text = page.extract_text()
                        if page_text:
                            page_texts.append(page_text)
                    
                    text = "\n".join(page_texts)
                    method = "pdfplumber"
                    
                    if len(text.strip()) > 50:
                        return text, method
                        
            except Exception:
                pass
            
            # 方法2: 使用PyPDF2作为备用
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    total_pages = len(pdf_reader.pages)
                    start_page = max(0, min_pages - 1)
                    end_page = min(total_pages, max_pages)
                    
                    page_texts = []
                    for i in range(start_page, end_page):
                        page = pdf_reader.pages[i]
                        page_text = page.extract_text()
                        if page_text:
                            page_texts.append(page_text)
                    
                    text = "\n".join(page_texts)
                    method = "PyPDF2"
                    
            except Exception:
                pass
            
        except Exception:
            pass
        
        return text, method
    
    def detect_document_type(self, text: str, filename: str) -> str:
        """检测文档类型"""
        book_keywords = self.config['document_detection']['book_keywords']
        paper_keywords = self.config['document_detection']['paper_keywords']
        
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        book_score = sum(1 for keyword in book_keywords if keyword.lower() in text_lower)
        paper_score = sum(1 for keyword in paper_keywords if keyword.lower() in text_lower)
        
        # 文件名也参与判断
        if any(keyword in filename_lower for keyword in ['journal', 'paper', 'article']):
            paper_score += 2
        if any(keyword in filename_lower for keyword in ['book', 'isbn', 'publisher']):
            book_score += 2
        
        return "paper" if paper_score > book_score else "book"
    
    async def analyze_with_ai(self, text: str, filename: str, doc_type: str) -> Dict[str, Any]:
        """使用AI分析文档信息"""
        api_config = self.config['ai_service']
        
        # 构建提示词
        if doc_type == "book":
            system_prompt = """你是一个专业的图书信息提取专家。请从给定的文本中提取以下信息：
- title: 书名（完整准确）
- author: 作者姓名
- publisher: 出版社名称
- year: 出版年份
- language: 原文语言（zh/en/etc）

请以JSON格式返回，如果某信息无法确定，请设为空字符串。
同时提供一个0-1之间的confidence置信度分数。"""
        else:
            system_prompt = """你是一个专业的学术论文信息提取专家。请从给定的文本中提取以下信息：
- title: 论文标题（完整准确）  
- author: 作者姓名（如多个作者可用"et al."）
- journal: 期刊或会议名称
- year: 发表年份
- language: 原文语言（zh/en/etc）

请以JSON格式返回，如果某信息无法确定，请设为空字符串。
同时提供一个0-1之间的confidence置信度分数。"""
        
        # 准备API请求
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_config['api_key']}"
        }
        
        # 限制文本长度
        max_chars = 3000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        user_content = f"""文件名: {filename}

文档内容:
{text}

请提取上述信息并以JSON格式返回。"""
        
        data = {
            "model": api_config["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                api_config["api_url"],
                headers=headers,
                json=data,
                timeout=api_config["timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # 尝试解析JSON
                try:
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        extracted_info = json.loads(json_str)
                        
                        # 确保必要字段存在
                        required_fields = ['title', 'author', 'year', 'confidence']
                        for field in required_fields:
                            if field not in extracted_info:
                                extracted_info[field] = ""
                        
                        return extracted_info
                    else:
                        return {"error": "JSON解析失败", "confidence": 0.0}
                        
                except json.JSONDecodeError:
                    return {"error": "JSON格式错误", "confidence": 0.0}
                    
            else:
                return {"error": f"API请求失败 (状态码: {response.status_code})", "confidence": 0.0}
                
        except Exception as e:
            return {"error": f"API调用异常: {str(e)}", "confidence": 0.0}
    
    def generate_filename(self, extracted_info: Dict[str, Any], doc_type: str) -> str:
        """生成新文件名"""
        try:
            # 获取命名模板
            if doc_type == "book":
                template = self.config['file_naming']['book_pattern']
            else:
                template = self.config['file_naming']['paper_pattern']
            
            # 调试输出
            console.print(f"[debug]原始模板: {template}")
            console.print(f"[debug]提取信息: {extracted_info}")
            
            # 清理和格式化字段
            clean_info = {}
            for key, value in extracted_info.items():
                if isinstance(value, str):
                    # 清理非法字符
                    clean_value = re.sub(r'[<>:"/\\|?*]', '_', value)
                    clean_value = re.sub(r'\s+', ' ', clean_value).strip()
                    # 如果值为空，提供默认值
                    if not clean_value:
                        if key == 'title':
                            clean_value = '未知标题'
                        elif key == 'author':
                            clean_value = '未知作者'
                        elif key == 'year':
                            clean_value = '未知年份'
                        elif key == 'publisher':
                            clean_value = '未知出版社'
                        elif key == 'journal':
                            clean_value = '未知期刊'
                        else:
                            clean_value = '未知'
                    clean_info[key] = clean_value
                else:
                    clean_info[key] = str(value) if value else '未知'
            
            console.print(f"[debug]清理后信息: {clean_info}")
            
            # 应用模板
            try:
                new_name = template.format(**clean_info)
                console.print(f"[debug]格式化成功: {new_name}")
            except KeyError as e:
                console.print(f"[debug]模板变量缺失: {e}")
                # 使用基本信息生成文件名
                title = clean_info.get('title', '未知标题')
                author = clean_info.get('author', '未知作者')
                year = clean_info.get('year', '')
                if year:
                    new_name = f"{title} - {author} ({year})"
                else:
                    new_name = f"{title} - {author}"
            except Exception as e:
                console.print(f"[debug]格式化异常: {e}")
                # 最后的备用方案
                title = clean_info.get('title', '未知标题')
                author = clean_info.get('author', '未知作者')
                new_name = f"{title} - {author}"
            
            # 确保文件名长度合理
            max_length = self.config['file_naming']['max_filename_length']
            if len(new_name) > max_length - 4:  # 减去.pdf的长度
                new_name = new_name[:max_length-4]
            
            result_filename = f"{new_name}.pdf"
            console.print(f"[debug]最终文件名: {result_filename}")
            return result_filename
            
        except Exception as e:
            console.print(f"[debug]generate_filename异常: {e}")
            import traceback
            traceback.print_exc()
            return "重命名失败.pdf"
    async def process_single_document(self, file_path: Path, min_pages: int, max_pages: int) -> Dict[str, Any]:
        """处理单个文档"""
        result = {
            "file_path": str(file_path),
            "filename": file_path.name,
            "success": False,
            "document_type": None,
            "extracted_info": {},
            "new_filename": None,
            "error": None,
            "needs_ocr": False
        }
        
        try:
            console.print(f"[blue]📄 处理文件: {file_path.name}")
            
            # 1. 提取PDF文本
            text, extraction_method = self.extract_pdf_text(file_path, min_pages, max_pages)
            
            # 检查文本质量
            min_text_length = self.config['text_extraction']['min_text_length']
            if not text or len(text.strip()) < min_text_length:
                result["needs_ocr"] = True
                result["error"] = "文本提取失败或文本过少，可能需要OCR处理"
                console.print(f"[yellow]⚠️ {result['error']}")
                return result
            
            console.print(f"[green]✅ 文本提取成功 (方法: {extraction_method}, 长度: {len(text)} 字符)")
            
            # 2. 检测文档类型
            doc_type = self.detect_document_type(text, file_path.name)
            result["document_type"] = doc_type
            
            console.print(f"[cyan]🔍 检测为: {'📚 书籍' if doc_type == 'book' else '📄 论文'}")
            
            # 3. AI分析提取信息
            extracted_info = await self.analyze_with_ai(text, file_path.name, doc_type)
            
            if "error" in extracted_info:
                result["error"] = extracted_info["error"]
                return result
            
            confidence = extracted_info.get('confidence', 0.0)
            if confidence < self.config['processing']['min_confidence']:
                result["error"] = f"AI分析置信度过低: {confidence:.2f}"
                return result
            
            result["extracted_info"] = extracted_info
            console.print(f"[green]✅ 信息提取成功 (置信度: {confidence:.2f})")
            
            # 4. 生成新文件名
            new_filename = self.generate_filename(extracted_info, doc_type)
            result["new_filename"] = new_filename
            result["success"] = True
            
            console.print(f"[cyan]📝 建议文件名: {new_filename}")
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    async def process_directory(self, input_dir: str, settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """处理目录中的PDF文件"""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            console.print(f"[red]❌ 输入目录不存在: {input_dir}")
            return []
        
        # 查找PDF文件（避免重复）
        pdf_files = list(input_path.rglob("*.pdf"))
        if not pdf_files:  # 如果没找到小写，再找大写
            pdf_files = list(input_path.rglob("*.PDF"))

        # 或者使用去重方式
        # pdf_files = list(set(input_path.rglob("*.pdf")) | set(input_path.rglob("*.PDF")))
        
        if not pdf_files:
            console.print("[yellow]⚠️ 未找到PDF文件")
            return []
        
        # 检查文件数量限制
        max_files = self.config['processing']['max_files_per_batch']
        if len(pdf_files) > max_files:
            console.print(f"[yellow]⚠️ 找到 {len(pdf_files)} 个PDF文件，但单次最多处理 {max_files} 个")
            if not Confirm.ask(f"是否只处理前 {max_files} 个文件？"):
                console.print("[yellow]操作已取消")
                return []
            pdf_files = pdf_files[:max_files]
        
        console.print(f"[blue]📚 开始处理 {len(pdf_files)} 个PDF文件")
        self.stats["total"] = len(pdf_files)
        
        results = []
        
        # 创建进度条
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("处理文件中...", total=len(pdf_files))
            
            for file_path in pdf_files:
                result = await self.process_single_document(
                    file_path, 
                    settings['min_pages'], 
                    settings['max_pages']
                )
                results.append(result)
                
                # 更新统计
                if result.get('success', False):
                    self.stats["successful"] += 1
                    if result['document_type'] == 'book':
                        self.stats["books"] += 1
                    else:
                        self.stats["papers"] += 1
                elif result.get('needs_ocr', False):
                    self.stats["ocr_needed"] += 1
                else:
                    self.stats["failed"] += 1
                
                progress.update(task, advance=1)
                await asyncio.sleep(0.1)
        
        return results
    
    def show_results_summary(self, results: List[Dict[str, Any]]):
        """显示处理结果摘要"""
        console.print(f"\n[cyan]{'='*80}")
        console.print("[bold]📊 处理结果摘要:")
        
        # 统计表格
        stats_table = Table(show_header=True, header_style="bold magenta")
        stats_table.add_column("统计项", style="cyan")
        stats_table.add_column("数量", justify="right", style="green")
        
        total = len(results)
        if total > 0:
            stats_table.add_row("总文件数", str(total))
            stats_table.add_row("✅ 成功处理", str(self.stats['successful']))
            stats_table.add_row("📚 书籍", str(self.stats['books']))
            stats_table.add_row("📄 论文", str(self.stats['papers']))
            stats_table.add_row("🔍 需要OCR", str(self.stats['ocr_needed']))
            stats_table.add_row("❌ 处理失败", str(self.stats['failed']))
        
        console.print(stats_table)
        
        # 成功结果详情
        successful = [r for r in results if r.get('success', False)]
        if successful:
            console.print(f"\n[bold]📋 成功处理的文件 (显示前5个):")
            
            for i, result in enumerate(successful[:5], 1):
                doc_type_icon = "📚" if result['document_type'] == 'book' else "📄"
                info = result['extracted_info']
                console.print(f"  {i}. {doc_type_icon} {result['filename']}")
                console.print(f"     📝 新名称: {result['new_filename']}")
                console.print(f"     📖 标题: {info.get('title', 'N/A')}")
                console.print(f"     ✍️ 作者: {info.get('author', 'N/A')}")
                console.print(f"     📅 年份: {info.get('year', 'N/A')}")
                console.print(f"     🎯 置信度: {info.get('confidence', 0):.2f}")
                console.print()
        
        # OCR需求文件
        ocr_needed = [r for r in results if r.get('needs_ocr', False)]
        if ocr_needed:
            console.print(f"[yellow]🔍 需要OCR处理的文件 ({len(ocr_needed)}个):")
            for result in ocr_needed[:3]:
                console.print(f"  • {result['filename']}")
            if len(ocr_needed) > 3:
                console.print(f"  ... 还有 {len(ocr_needed) - 3} 个文件")
        
        # 失败文件
        failed = [r for r in results if not r.get('success', False) and not r.get('needs_ocr', False)]
        if failed:
            console.print(f"\n[red]❌ 处理失败的文件:")
            for result in failed[:3]:
                console.print(f"  • {result['filename']}: {result.get('error', '未知错误')}")
    
    def handle_ocr_files(self, ocr_files: List[Dict[str, Any]], output_dir: str, same_directory: bool):
        """处理需要OCR的文件"""
        if not ocr_files:
            return
        
        ocr_prefix = self.config['file_naming']['ocr_prefix']
        
        for file_info in ocr_files:
            original_path = Path(file_info['file_path'])
            ocr_filename = f"{ocr_prefix}_{original_path.name}"
            
            try:
                if same_directory:
                    # 直接重命名原文件
                    new_path = original_path.parent / ocr_filename
                    original_path.rename(new_path)
                    console.print(f"[yellow]🔄 {original_path.name} -> {ocr_filename}")
                else:
                    # 复制到输出目录
                    output_path = Path(output_dir) / ocr_filename
                    shutil.copy2(original_path, output_path)
                    console.print(f"[yellow]📄 复制并标记: {ocr_filename}")
            except Exception as e:
                console.print(f"[red]❌ OCR文件处理失败 {original_path.name}: {e}")
    
    async def execute_rename(self, results: List[Dict[str, Any]], settings: Dict[str, Any]):
        """执行文件重命名"""
        successful_results = [r for r in results if r.get('success', False) and r.get('new_filename')]
        ocr_needed_results = [r for r in results if r.get('needs_ocr', False)]
        
        if not successful_results and not ocr_needed_results:
            console.print("[yellow]⚠️ 没有需要重命名的文件")
            return
        
        output_dir = settings['output_dir']
        same_directory = settings['same_directory']
        dry_run = self.config['processing']['dry_run']
        backup = self.config['processing']['backup_original'] and not same_directory
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        console.print(f"\n[cyan]{'='*80}")
        console.print(f"[cyan]🚀 {'模拟执行' if dry_run else '开始执行'}重命名操作...")
        
        if same_directory:
            console.print("[yellow]⚠️ 输入输出目录相同，将直接重命名原文件")
        
        success_count = 0
        error_count = 0
        
        # 处理成功分析的文件
        for result in successful_results:
            original_path = Path(result['file_path'])
            new_filename = result['new_filename']
            
            if same_directory:
                new_path = original_path.parent / new_filename
            else:
                new_path = output_path / new_filename
            
            try:
                if dry_run:
                    console.print(f"[blue]🔍 [模拟] {original_path.name} -> {new_filename}")
                else:
                    # 备份原文件
                    if backup:
                        backup_dir = Path('data/backup')
                        backup_dir.mkdir(parents=True, exist_ok=True)
                        backup_path = backup_dir / original_path.name
                        if not backup_path.exists():
                            shutil.copy2(original_path, backup_path)
                    
                    if same_directory:
                        # 直接重命名
                        original_path.rename(new_path)
                    else:
                        # 复制到输出目录
                        shutil.copy2(original_path, new_path)
                    
                    console.print(f"[green]✅ {original_path.name} -> {new_filename}")
                
                success_count += 1
                
            except Exception as e:
                console.print(f"[red]❌ 处理失败 {original_path.name}: {e}")
                error_count += 1
        
        # 处理需要OCR的文件
        if not dry_run:
            self.handle_ocr_files(ocr_needed_results, output_dir, same_directory)
        else:
            for file_info in ocr_needed_results:
                ocr_prefix = self.config['file_naming']['ocr_prefix']
                original_name = Path(file_info['file_path']).name
                console.print(f"[blue]🔍 [模拟] {original_name} -> {ocr_prefix}_{original_name}")
        
        # 显示最终统计
        console.print(f"\n[cyan]{'='*80}")
        console.print(f"[bold]🎯 {'模拟' if dry_run else '实际'}重命名完成:")
        console.print(f"✅ 成功: {success_count}")
        console.print(f"🔍 OCR标记: {len(ocr_needed_results)}")
        console.print(f"❌ 失败: {error_count}")
        
        if dry_run:
            console.print("[blue]🔍 这是模拟运行，没有实际修改文件")
            console.print("[blue]💡 要实际执行，请在.env中设置 DRY_RUN=false")

async def main():
    """主函数"""
    try:
        # 初始化重命名器
        renamer = DocumentRenamer()
        
        # 检查配置
        is_valid, message = renamer.config_manager.validate_config()
        if not is_valid:
            console.print(f"[red]❌ 配置验证失败: {message}")
            console.print("[blue]💡 请检查 .env 文件中的API配置")
            input("按回车键退出...")
            return 1
        
        console.print(f"[green]✅ {message}")
        
        if not Confirm.ask("\n是否继续处理？"):
            console.print("[yellow]❌ 操作已取消")
            input("按回车键退出...")
            return 0
        
        # 获取用户设置
        settings = renamer.get_user_settings()
        
        # 确保输入目录存在
        input_path = Path(settings['input_dir'])
        if not input_path.exists():
            console.print(f"[red]❌ 输入目录不存在: {settings['input_dir']}")
            console.print(f"[blue]💡 已创建目录，请将PDF文件放入后重新运行")
            input_path.mkdir(parents=True, exist_ok=True)
            input("按回车键退出...")
            return 1
        
        # 开始批量处理
        console.print(f"\n[blue]🔍 开始处理目录: {settings['input_dir']}")
        console.print(f"[blue]📄 页码范围: {settings['min_pages']}-{settings['max_pages']}页")
        
        results = await renamer.process_directory(settings['input_dir'], settings)
        
        if not results:
            console.print("[yellow]⚠️ 没有找到可处理的文件")
            input("按回车键退出...")
            return 0
        
        # 显示结果摘要
        renamer.show_results_summary(results)
        
        # 询问是否执行重命名
        processable_results = [r for r in results if r.get('success', False) or r.get('needs_ocr', False)]
        if processable_results:
            success_count = len([r for r in results if r.get('success', False)])
            ocr_count = len([r for r in results if r.get('needs_ocr', False)])
            
            console.print(f"\n[green]🎉 可处理 {len(processable_results)} 个文件！")
            console.print(f"  • ✅ 成功分析: {success_count}个")
            console.print(f"  • 🔍 需要OCR: {ocr_count}个")
            
            if Confirm.ask("🤔 是否执行重命名操作？"):
                if not renamer.config['processing']['dry_run'] and not settings['same_directory']:
                    warning_msg = (
                        "[red]⚠️ 警告: 这将复制文件到输出目录！\n"
                        f"原文件将保留，重命名后的文件会保存到: {settings['output_dir']}"
                    )
                    console.print(Panel(warning_msg, style="red", title="重要提醒"))
                    
                    if not Confirm.ask("[red]确定要执行文件操作吗？"):
                        console.print("[yellow]❌ 操作已取消")
                        input("按回车键退出...")
                        return 0
                elif settings['same_directory']:
                    warning_msg = (
                        "[yellow]⚠️ 注意: 将直接修改原文件名！\n"
                        "建议先备份重要文件"
                    )
                    console.print(Panel(warning_msg, style="yellow", title="重要提醒"))
                    
                    if not Confirm.ask("[yellow]确定要直接重命名原文件吗？"):
                        console.print("[yellow]❌ 操作已取消")
                        input("按回车键退出...")
                        return 0
                
                await renamer.execute_rename(results, settings)
            else:
                console.print("[yellow]❌ 重命名操作已取消")
        else:
            console.print("[red]❌ 没有可处理的文件")
        
        console.print(f"\n[green]🎉 程序执行完成！")
        input("按回车键退出...")
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ 程序被用户中断")
        input("按回车键退出...")
        return 1
    except Exception as e:
        console.print(f"\n[red]❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
        return 1

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        # Windows平台设置事件循环策略
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        sys.exit(asyncio.run(main()))
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")
        sys.exit(1)