"""
邮件消息数据模型

本模块定义了邮件消息的完整数据结构,提供邮件数据的序列化、验证和CSV转换功能。
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from email.utils import parseaddr

from .attachment import Attachment


@dataclass
class EmailMessage:
    """
    邮件消息数据模型
    
    Attributes:
        email_account: 邮箱账户地址
        message_id: 邮件唯一标识符
        thread_id: 会话/线程ID
        subject: 邮件主题
        date: 发送日期时间(UTC时区)
        from_address: 发件人邮箱地址
        from_name: 发件人显示名称
        to_addresses: 收件人邮箱地址列表
        to_names: 收件人显示名称列表
        cc_addresses: 抄送人邮箱地址列表
        body_text: 纯文本正文
        body_html: HTML正文(可选)
        has_attachment: 是否包含附件
        attachments: 附件列表
        labels: 邮件标签/文件夹列表
        is_read: 是否已读
        uid: IMAP UID(用于防止重复处理)
    
    Examples:
        >>> msg = EmailMessage(
        ...     email_account="user@gmail.com",
        ...     message_id="<abc123@mail.gmail.com>",
        ...     subject="测试邮件",
        ...     date=datetime.now(),
        ...     from_address="sender@example.com",
        ...     from_name="发件人"
        ... )
        >>> msg.add_attachment(attachment)
        >>> row = msg.to_csv_row()
    """
    
    # 必需字段
    email_account: str
    message_id: str
    subject: str
    date: datetime
    from_address: str
    
    # 可选字段
    thread_id: Optional[str] = None
    from_name: Optional[str] = None
    to_addresses: List[str] = field(default_factory=list)
    to_names: List[str] = field(default_factory=list)
    cc_addresses: List[str] = field(default_factory=list)
    body_text: str = ""
    body_html: Optional[str] = None
    has_attachment: bool = False
    attachments: List[Attachment] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    is_read: bool = False
    uid: Optional[int] = None
    
    def __post_init__(self):
        """数据验证"""
        # 验证必需字段
        if not self.message_id:
            raise ValueError("邮件message_id不能为空")
        
        if not self.email_account:
            raise ValueError("邮箱账户email_account不能为空")
        
        # 验证邮箱格式
        if not self._is_valid_email(self.email_account):
            raise ValueError(f"无效的邮箱账户格式: {self.email_account}")
        
        if not self._is_valid_email(self.from_address):
            raise ValueError(f"无效的发件人邮箱格式: {self.from_address}")
        
        # 验证日期
        if not isinstance(self.date, datetime):
            raise ValueError("date必须是datetime对象")
        
        # 验证附件列表
        if not isinstance(self.attachments, list):
            raise ValueError("attachments必须是列表")
        
        for att in self.attachments:
            if not isinstance(att, Attachment):
                raise ValueError("attachments列表中必须包含Attachment对象")
        
        # 更新has_attachment标志
        self.has_attachment = len(self.attachments) > 0
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            如果格式有效返回True,否则False
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def to_dict(self) -> dict:
        """
        转换为字典
        
        Returns:
            包含所有邮件数据的字典
            
        Examples:
            >>> msg.to_dict()
            {'email_account': 'user@gmail.com', 'message_id': '<abc>', ...}
        """
        return {
            'email_account': self.email_account,
            'message_id': self.message_id,
            'thread_id': self.thread_id,
            'subject': self.subject,
            'date': self.date.isoformat(),
            'from_address': self.from_address,
            'from_name': self.from_name,
            'to_addresses': self.to_addresses,
            'to_names': self.to_names,
            'cc_addresses': self.cc_addresses,
            'body_text': self.body_text,
            'body_html': self.body_html,
            'has_attachment': self.has_attachment,
            'attachments': [att.to_dict() for att in self.attachments],
            'labels': self.labels,
            'is_read': self.is_read,
            'uid': self.uid
        }
    
    def to_csv_row(self) -> dict:
        """
        转换为CSV行格式(扁平化数据)
        
        Returns:
            适用于CSV写入的字典,包含以下键:
            - email_account
            - message_id
            - thread_id
            - subject
            - date (格式: "YYYY-MM-DD HH:MM:SS")
            - from (格式: "名称 <邮箱>" 或 "邮箱")
            - to (多个收件人用分号分隔)
            - cc (多个抄送人用分号分隔)
            - body_text
            - has_attachment ("True"/"False")
            - attachment_names (多个附件用分号分隔)
            - attachment_count
            - labels (多个标签用分号分隔)
            
        Examples:
            >>> row = msg.to_csv_row()
            >>> row['from']
            '张三 <zhangsan@example.com>'
        """
        # 格式化发件人
        from_field = self._format_email_with_name(
            self.from_address, 
            self.from_name
        )
        
        # 格式化收件人
        to_field = self._format_email_list(
            self.to_addresses, 
            self.to_names
        )
        
        # 格式化抄送人
        cc_field = self._format_email_list(
            self.cc_addresses, 
            []
        )
        
        # 格式化日期
        date_str = self.date.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            'email_account': self.email_account,
            'message_id': self.message_id,
            'thread_id': self.thread_id or '',
            'subject': self.subject,
            'date': date_str,
            'from': from_field,
            'to': to_field,
            'cc': cc_field,
            'body_text': self.body_text,
            'has_attachment': str(self.has_attachment),
            'attachment_names': self.get_attachment_names(),
            'attachment_count': len(self.attachments),
            'labels': ';'.join(self.labels)
        }
    
    @staticmethod
    def _format_email_with_name(email: str, name: Optional[str]) -> str:
        """
        格式化邮箱和名称
        
        Args:
            email: 邮箱地址
            name: 显示名称
            
        Returns:
            格式化后的字符串: "名称 <邮箱>" 或 "邮箱"
        """
        if name:
            return f"{name} <{email}>"
        return email
    
    @staticmethod
    def _format_email_list(
        addresses: List[str], 
        names: List[str]
    ) -> str:
        """
        格式化邮箱列表
        
        Args:
            addresses: 邮箱地址列表
            names: 显示名称列表
            
        Returns:
            用分号分隔的字符串
        """
        result = []
        for i, addr in enumerate(addresses):
            name = names[i] if i < len(names) else None
            if name:
                result.append(f"{name} <{addr}>")
            else:
                result.append(addr)
        return ';'.join(result)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EmailMessage':
        """
        从字典创建实例
        
        Args:
            data: 包含邮件数据的字典
            
        Returns:
            EmailMessage实例
            
        Examples:
            >>> data = {
            ...     'email_account': 'user@gmail.com',
            ...     'message_id': '<abc>',
            ...     'subject': '测试',
            ...     'date': '2024-01-15T14:30:25',
            ...     'from_address': 'sender@example.com'
            ... }
            >>> msg = EmailMessage.from_dict(data)
        """
        # 转换日期
        date = data['date']
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        
        # 转换附件
        attachments = []
        if 'attachments' in data:
            attachments = [
                Attachment.from_dict(att_data) 
                for att_data in data['attachments']
            ]
        
        return cls(
            email_account=data['email_account'],
            message_id=data['message_id'],
            thread_id=data.get('thread_id'),
            subject=data['subject'],
            date=date,
            from_address=data['from_address'],
            from_name=data.get('from_name'),
            to_addresses=data.get('to_addresses', []),
            to_names=data.get('to_names', []),
            cc_addresses=data.get('cc_addresses', []),
            body_text=data.get('body_text', ''),
            body_html=data.get('body_html'),
            has_attachment=data.get('has_attachment', False),
            attachments=attachments,
            labels=data.get('labels', []),
            is_read=data.get('is_read', False),
            uid=data.get('uid')
        )
    
    def add_attachment(self, attachment: Attachment) -> None:
        """
        添加附件
        
        Args:
            attachment: Attachment对象
            
        Raises:
            TypeError: 如果参数不是Attachment对象
            
        Examples:
            >>> msg = EmailMessage(...)
            >>> att = Attachment("file.pdf", "application/pdf", 1024)
            >>> msg.add_attachment(att)
        """
        if not isinstance(attachment, Attachment):
            raise TypeError("参数必须是Attachment对象")
        
        self.attachments.append(attachment)
        self.has_attachment = True
    
    def get_attachment_names(self) -> str:
        """
        返回所有附件名称的字符串(用分号分隔)
        
        Returns:
            附件名称字符串,如 "file1.pdf;image.png"
            
        Examples:
            >>> msg.get_attachment_names()
            'report.pdf;photo.jpg'
        """
        return ';'.join([att.filename for att in self.attachments])
    
    def __repr__(self) -> str:
        """
        字符串表示
        
        Returns:
            邮件的字符串表示
        """
        att_info = f", {len(self.attachments)} attachments" if self.has_attachment else ""
        return (
            f"EmailMessage(id='{self.message_id}', "
            f"subject='{self.subject}', "
            f"from='{self.from_address}'{att_info})"
        )