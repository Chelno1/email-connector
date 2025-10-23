"""
数据模型模块

本模块提供邮件数据的核心数据结构:
- EmailMessage: 邮件消息模型
- Attachment: 附件模型
"""

from .email_message import EmailMessage
from .attachment import Attachment

__all__ = ['EmailMessage', 'Attachment']
__version__ = '1.0.0'