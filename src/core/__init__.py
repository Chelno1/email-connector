"""
核心功能模块

包含IMAP客户端、邮件解析器和CSV写入器等核心组件。
"""

from .imap_client import IMAPClient, IMAPError
from .email_parser import EmailParser, EmailParseError
from .csv_writer import CSVWriter, CSVWriteError, create_csv_writer

__all__ = [
    'IMAPClient',
    'IMAPError',
    'EmailParser',
    'EmailParseError',
    'CSVWriter',
    'CSVWriteError',
    'create_csv_writer'
]