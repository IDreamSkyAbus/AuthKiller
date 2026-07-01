#!/usr/bin/env python3
"""
THINKER GUI 启动脚本
用于启动基于Tkinter的桌面GUI应用
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 导入并运行GUI应用
from authkiller.gui.thinker_app import main

if __name__ == '__main__':
    main()