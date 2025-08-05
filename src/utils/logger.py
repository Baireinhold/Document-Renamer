#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具
"""

import logging
import sys
from pathlib import Path

def setup_logger():
    """设置日志系统"""
    # 创建日志目录
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)