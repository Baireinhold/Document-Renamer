#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动器 - 智能文档重命名工具
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """主启动函数"""
    print("🚀 启动智能文档重命名工具...")
    
    try:
        # 检查.env文件
        env_file = project_root / ".env"
        if not env_file.exists():
            print("⚠️ 未找到.env配置文件")
            print("📝 请创建.env文件并配置API密钥")
            input("按回车键退出...")
            return 0
        
        # 导入并运行主程序
        from src.main import main as main_func
        import asyncio
        
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        return asyncio.run(main_func())
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("💡 请确保已安装所有依赖: pip install -r requirements.txt")
        input("按回车键退出...")
        return 1
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        input("按回车键退出...")
        return 1

if __name__ == "__main__":
    sys.exit(main())