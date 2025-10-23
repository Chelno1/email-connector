#!/usr/bin/env python3
"""
Email Connector - IMAP邮件提取和CSV导出工具

这是项目的主入口点,提供简洁的命令行界面。

使用示例:
    python email_connector.py --help
    python email_connector.py --unseen --limit 10
    python email_connector.py --from-date 2024-01-01 --to-date 2024-01-31
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.main import main

if __name__ == '__main__':
    main()