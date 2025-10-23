"""
邮件解析器模块

职责:
- 解析MIME格式邮件
- 提取邮件头部信息(发件人、收件人、主题、日期等)
- 提取邮件正文(纯文本和HTML)
- 解析和提取附件
- 处理多种字符编码
- 清洗HTML内容
"""

import email
import re
import html
from email import policy
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from email.message import Message
from typing import List, Optional, Tuple, Generator
from datetime import datetime, timezone
from html.parser import HTMLParser
from io import StringIO

from src.models.email_message import EmailMessage
from src.models.attachment import Attachment
from src.utils.logger import get_logger, log_performance


class EmailParseError(Exception):
    """邮件解析异常"""
    pass


class HTMLStripper(HTMLParser):
    """HTML标签移除器"""
    
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()
        self.skip_tags = {'script', 'style', 'head', 'meta', 'link'}
        self.current_tag = None
    
    def handle_starttag(self, tag, attrs):
        """处理开始标签"""
        self.current_tag = tag
        # 在块级元素前添加换行
        if tag in {'p', 'div', 'br', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.text.write('\n')
    
    def handle_endtag(self, tag):
        """处理结束标签"""
        self.current_tag = None
        # 在块级元素后添加换行
        if tag in {'p', 'div', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.text.write('\n')
    
    def handle_data(self, data):
        """处理文本数据"""
        # 跳过script、style等标签内的内容
        if self.current_tag not in self.skip_tags:
            self.text.write(data)
    
    def get_text(self) -> str:
        """获取提取的文本"""
        return self.text.getvalue()


class EmailParser:
    """
    邮件解析器类
    
    负责解析MIME格式邮件,提取邮件元数据、正文和附件。
    
    Attributes:
        email_account: 邮箱账户地址
        logger: 日志记录器
        max_text_length: 正文最大长度(防止内存溢出)
    
    Examples:
        >>> parser = EmailParser("user@gmail.com")
        >>> msg = parser.parse(raw_email_bytes, uid=12345)
        >>> print(msg.subject)
        '邮件主题'
    """
    
    def __init__(
        self, 
        email_account: str, 
        logger=None,
        max_text_length: int = 50000
    ):
        """
        初始化邮件解析器
        
        Args:
            email_account: 邮箱账户地址
            logger: 日志记录器(可选)
            max_text_length: 正文最大长度(默认50000字符)
        """
        self.email_account = email_account
        self.logger = logger or get_logger(__name__)
        self.max_text_length = max_text_length
    
    @log_performance
    def parse(self, raw_email: bytes, uid: Optional[int] = None) -> EmailMessage:
        """
        解析原始邮件数据
        
        Args:
            raw_email: 原始邮件字节数据
            uid: IMAP UID(可选)
            
        Returns:
            EmailMessage对象
            
        Raises:
            EmailParseError: 解析失败时抛出
            
        Examples:
            >>> parser = EmailParser("user@gmail.com")
            >>> msg = parser.parse(raw_email_bytes)
            >>> print(f"主题: {msg.subject}")
        """
        try:
            # 使用policy.default解析邮件,支持更好的Unicode处理
            msg = email.message_from_bytes(raw_email, policy=policy.default)
            
            # 提取消息ID
            message_id = msg.get('Message-ID', '').strip()
            if not message_id:
                # 如果没有Message-ID,使用UID或生成一个
                if uid:
                    message_id = f"<uid-{uid}@{self.email_account}>"
                else:
                    message_id = f"<generated-{id(msg)}@{self.email_account}>"
            
            # 提取主题
            subject = self._decode_header(msg.get('Subject', '(无主题)'))
            
            # 提取日期
            date = self._parse_date(msg.get('Date'))
            
            # 提取发件人
            from_header = msg.get('From', '')
            from_address, from_name = self._extract_email_address(from_header)
            
            # 提取收件人
            to_addresses, to_names = self._parse_addresses(msg.get('To', ''))
            
            # 提取抄送
            cc_addresses, _ = self._parse_addresses(msg.get('Cc', ''))
            
            # 提取正文
            body_text, body_html = self._parse_body(msg)
            
            # 提取附件
            attachments = self._parse_attachments(msg)
            
            # 提取线程ID(如果有)
            thread_id = msg.get('In-Reply-To', '').strip()
            
            # 提取标签(Gmail特定)
            labels = self._parse_labels(msg)
            
            # 创建EmailMessage对象
            email_msg = EmailMessage(
                email_account=self.email_account,
                message_id=message_id,
                thread_id=thread_id or None,
                subject=subject,
                date=date,
                from_address=from_address,
                from_name=from_name,
                to_addresses=to_addresses,
                to_names=to_names,
                cc_addresses=cc_addresses,
                body_text=body_text,
                body_html=body_html,
                has_attachment=len(attachments) > 0,
                attachments=attachments,
                labels=labels,
                uid=uid
            )
            
            self.logger.debug(f"成功解析邮件: {message_id}")
            return email_msg
            
        except Exception as e:
            self.logger.error(f"解析邮件失败: {e}")
            raise EmailParseError(f"邮件解析错误: {e}")
    
    def parse_batch(
        self, 
        raw_emails: List[Tuple[int, bytes]]
    ) -> Generator[EmailMessage, None, None]:
        """
        批量解析邮件(生成器模式)
        
        Args:
            raw_emails: (uid, raw_email)元组列表
            
        Yields:
            EmailMessage对象
            
        Examples:
            >>> parser = EmailParser("user@gmail.com")
            >>> emails = [(1, raw1), (2, raw2), (3, raw3)]
            >>> for msg in parser.parse_batch(emails):
            ...     print(msg.subject)
        """
        total = len(raw_emails)
        self.logger.info(f"开始批量解析 {total} 封邮件")
        
        for i, (uid, raw_email) in enumerate(raw_emails, 1):
            try:
                msg = self.parse(raw_email, uid=uid)
                self.logger.debug(f"批量解析进度: {i}/{total}")
                yield msg
            except EmailParseError as e:
                self.logger.warning(f"跳过无法解析的邮件 UID={uid}: {e}")
                continue
    
    def _decode_header(self, header: str) -> str:
        """
        解码邮件头部
        
        处理RFC 2047编码的头部,如 =?UTF-8?B?...?=
        
        Args:
            header: 原始头部字符串
            
        Returns:
            解码后的字符串
        """
        if not header:
            return ''
        
        try:
            decoded_parts = []
            for part, encoding in decode_header(header):
                if isinstance(part, bytes):
                    # 尝试使用指定的编码
                    if encoding:
                        try:
                            decoded_parts.append(part.decode(encoding))
                        except (UnicodeDecodeError, LookupError):
                            # 如果指定编码失败,尝试常见编码
                            decoded_parts.append(self._decode_bytes(part))
                    else:
                        decoded_parts.append(self._decode_bytes(part))
                else:
                    decoded_parts.append(str(part))
            
            return ''.join(decoded_parts).strip()
            
        except Exception as e:
            self.logger.warning(f"头部解码失败: {e}, 使用原始值")
            return str(header)
    
    def _decode_bytes(self, data: bytes) -> str:
        """
        解码字节数据,尝试多种编码
        
        Args:
            data: 字节数据
            
        Returns:
            解码后的字符串
        """
        # 常见编码列表
        encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'iso-8859-1', 'windows-1252']
        
        for encoding in encodings:
            try:
                return data.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 如果所有编码都失败,使用替换策略
        return data.decode('utf-8', errors='replace')
    
    def _parse_date(self, date_header: Optional[str]) -> datetime:
        """
        解析邮件日期
        
        Args:
            date_header: Date头部字符串
            
        Returns:
            datetime对象(UTC时区)
        """
        if not date_header:
            # 如果没有日期,使用当前时间
            return datetime.now(timezone.utc)
        
        try:
            # 使用email.utils.parsedate_to_datetime解析RFC 2822日期
            dt = parsedate_to_datetime(date_header)
            
            # 转换为UTC时区
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            
            return dt
            
        except Exception as e:
            self.logger.warning(f"日期解析失败: {e}, 使用当前时间")
            return datetime.now(timezone.utc)
    
    def _extract_email_address(
        self, 
        address_header: str
    ) -> Tuple[str, Optional[str]]:
        """
        从地址字段提取邮箱和显示名称
        
        Args:
            address_header: 地址头部字符串,如 "张三 <zhangsan@example.com>"
            
        Returns:
            (邮箱地址, 显示名称)元组
        """
        if not address_header:
            return '', None
        
        try:
            # 先解码头部
            decoded = self._decode_header(address_header)
            
            # 使用parseaddr解析
            name, email_addr = parseaddr(decoded)
            
            # 清理名称
            name = name.strip() if name else None
            email_addr = email_addr.strip().lower()
            
            return email_addr, name
            
        except Exception as e:
            self.logger.warning(f"地址解析失败: {e}")
            return address_header, None
    
    def _parse_addresses(
        self, 
        addresses_header: str
    ) -> Tuple[List[str], List[str]]:
        """
        解析地址列表(支持多个收件人)
        
        Args:
            addresses_header: 地址列表字符串
            
        Returns:
            (邮箱地址列表, 显示名称列表)元组
        """
        if not addresses_header:
            return [], []
        
        addresses = []
        names = []
        
        # 解码头部
        decoded = self._decode_header(addresses_header)
        
        # 分割多个地址(逗号分隔)
        for addr in decoded.split(','):
            addr = addr.strip()
            if addr:
                email_addr, name = self._extract_email_address(addr)
                if email_addr:
                    addresses.append(email_addr)
                    names.append(name or '')
        
        return addresses, names
    
    def _parse_body(
        self,
        msg: Message
    ) -> Tuple[str, Optional[str]]:
        """
        解析邮件正文
        
        Args:
            msg: email.message.Message对象
            
        Returns:
            (纯文本正文, HTML正文)元组
        """
        text_plain = ''
        text_html = None
        
        try:
            if msg.is_multipart():
                # 处理multipart邮件
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition', ''))
                    
                    # 跳过附件
                    if 'attachment' in content_disposition:
                        continue
                    
                    # 提取纯文本
                    if content_type == 'text/plain' and not text_plain:
                        text_plain = self._extract_text_content(part)
                    
                    # 提取HTML
                    elif content_type == 'text/html' and not text_html:
                        text_html = self._extract_text_content(part)
            else:
                # 处理单部分邮件
                content_type = msg.get_content_type()
                
                if content_type == 'text/plain':
                    text_plain = self._extract_text_content(msg)
                elif content_type == 'text/html':
                    text_html = self._extract_text_content(msg)
            
            # 如果只有HTML没有纯文本,从HTML提取
            if not text_plain and text_html:
                text_plain = self._clean_html(text_html)
            
            # 限制长度
            if len(text_plain) > self.max_text_length:
                text_plain = text_plain[:self.max_text_length] + '...(已截断)'
            
            if text_html and len(text_html) > self.max_text_length:
                text_html = text_html[:self.max_text_length] + '...(已截断)'
            
        except Exception as e:
            self.logger.warning(f"正文解析失败: {e}")
        
        return text_plain, text_html
    
    def _extract_text_content(self, part: Message) -> str:
        """
        从邮件部分提取文本内容
        
        Args:
            part: email.message.Message部分
            
        Returns:
            解码后的文本
        """
        try:
            payload = part.get_payload(decode=True)
            
            if payload is None:
                return ''
            
            # 确保payload是bytes类型
            if not isinstance(payload, bytes):
                return str(payload)
            
            # 获取字符集
            charset = part.get_content_charset()
            
            if charset:
                try:
                    return payload.decode(charset, errors='replace')
                except (UnicodeDecodeError, LookupError):
                    pass
            
            # 如果没有指定字符集或解码失败,尝试自动检测
            return self._decode_bytes(payload)
            
        except Exception as e:
            self.logger.warning(f"内容提取失败: {e}")
            return ''
    
    def _clean_html(self, html_text: str) -> str:
        """
        清洗HTML内容,转换为纯文本
        
        Args:
            html_text: HTML文本
            
        Returns:
            纯文本
        """
        try:
            # 使用HTMLStripper移除标签
            stripper = HTMLStripper()
            stripper.feed(html_text)
            text = stripper.get_text()
            
            # 解码HTML实体
            text = html.unescape(text)
            
            # 清理多余的空白
            text = re.sub(r'\n\s*\n', '\n\n', text)  # 多个空行变为两个
            text = re.sub(r' +', ' ', text)  # 多个空格变为一个
            text = text.strip()
            
            return text
            
        except Exception as e:
            self.logger.warning(f"HTML清洗失败: {e}")
            return html_text
    
    def _parse_attachments(
        self,
        msg: Message
    ) -> List[Attachment]:
        """
        解析并提取附件
        
        Args:
            msg: email.message.Message对象
            
        Returns:
            Attachment对象列表
        """
        attachments = []
        
        try:
            for part in msg.walk():
                # 检查是否为附件
                if not self._is_attachment(part):
                    continue
                
                # 提取附件信息
                filename = self._get_attachment_filename(part)
                if not filename:
                    self.logger.debug("跳过无文件名的附件")
                    continue
                
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)
                
                if payload is None or not isinstance(payload, bytes):
                    self.logger.debug(f"跳过无内容的附件: {filename}")
                    continue
                
                size = len(payload)
                
                # 创建Attachment对象
                attachment = Attachment(
                    filename=filename,
                    content_type=content_type,
                    size=size,
                    content=payload
                )
                
                attachments.append(attachment)
                self.logger.debug(f"提取附件: {filename} ({size} bytes)")
                
        except Exception as e:
            self.logger.warning(f"附件解析失败: {e}")
        
        return attachments
    
    def _is_attachment(self, part: Message) -> bool:
        """
        判断是否为附件
        
        Args:
            part: email.message.Message部分
            
        Returns:
            是否为附件
        """
        content_disposition = str(part.get('Content-Disposition', ''))
        
        # 检查Content-Disposition头部
        if 'attachment' in content_disposition.lower():
            return True
        
        # 某些内联图片也算附件
        if 'inline' in content_disposition.lower():
            # 检查是否有文件名
            filename = part.get_filename()
            return filename is not None
        
        return False
    
    def _get_attachment_filename(
        self,
        part: Message
    ) -> Optional[str]:
        """
        提取附件文件名
        
        处理RFC 2231编码的文件名
        
        Args:
            part: email.message.Message部分
            
        Returns:
            文件名或None
        """
        filename = part.get_filename()
        
        if not filename:
            return None
        
        # 解码文件名
        try:
            if isinstance(filename, str):
                # 可能是RFC 2047编码
                filename = self._decode_header(filename)
            else:
                # 应该已经是字符串,但以防万一
                filename = str(filename)
            
            # 清理文件名中的路径分隔符
            filename = filename.replace('/', '_').replace('\\', '_')
            
            return filename
            
        except Exception as e:
            self.logger.warning(f"文件名解码失败: {e}")
            return 'unknown'
    
    def _parse_labels(self, msg: Message) -> List[str]:
        """
        解析邮件标签(Gmail特定)
        
        Args:
            msg: email.message.Message对象
            
        Returns:
            标签列表
        """
        labels = []
        
        # Gmail的X-Gmail-Labels头部
        gmail_labels = msg.get('X-Gmail-Labels', '')
        if gmail_labels:
            labels = [label.strip() for label in gmail_labels.split(',')]
        
        return labels