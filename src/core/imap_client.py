"""
IMAP客户端模块

职责:
- 建立和管理IMAP连接
- 提供邮件搜索和获取接口
- 处理IMAP协议相关操作
- 邮件状态管理(已读/未读/删除)
- 支持上下文管理器
"""

import imaplib
import socket
import threading
from datetime import datetime
from typing import List, Optional, Generator, Dict, Any, Tuple
from email.utils import parsedate_to_datetime

from ..utils.config_manager import ConfigManager
from ..utils.logger import get_logger, log_performance


# ==================== 异常类定义 ====================

class IMAPError(Exception):
    """IMAP操作基础异常"""
    pass


class IMAPConnectionError(IMAPError):
    """IMAP连接异常"""
    pass


class IMAPAuthenticationError(IMAPError):
    """IMAP认证异常"""
    pass


class IMAPOperationError(IMAPError):
    """IMAP操作异常"""
    pass


# ==================== IMAP客户端类 ====================

class IMAPClient:
    """
    IMAP客户端类
    
    提供完整的IMAP邮件操作功能,包括连接管理、邮件搜索、
    批量获取、状态管理等。支持上下文管理器模式。
    
    Attributes:
        config: ConfigManager实例
        logger: 日志记录器
        imap: IMAP连接对象
        is_connected: 连接状态
        current_folder: 当前选中的文件夹
        
    Examples:
        >>> config = ConfigManager()
        >>> with IMAPClient(config) as client:
        ...     client.connect()
        ...     email, password = config.get_email_credentials()
        ...     client.login(email, password)
        ...     uids = client.search_messages()
        ...     for raw_email in client.fetch_messages_batch(uids):
        ...         # 处理邮件
        ...         pass
    """
    
    def __init__(self, config_manager: ConfigManager, logger=None):
        """
        初始化IMAP客户端
        
        Args:
            config_manager: 配置管理器实例
            logger: 日志记录器(可选)
        """
        self.config = config_manager
        self.logger = logger or get_logger(__name__)
        self.imap: Optional[imaplib.IMAP4] = None
        self.is_connected = False
        self.is_authenticated = False
        self.current_folder: Optional[str] = None
        
        # 线程锁,用于保证线程安全
        self._lock = threading.RLock()
        
        self.logger.debug("IMAPClient实例已创建")
    
    # ==================== 连接管理 ====================
    
    @log_performance
    def connect(self) -> bool:
        """
        连接到IMAP服务器
        
        根据配置建立到IMAP服务器的连接(支持SSL/TLS)。
        
        Returns:
            True 如果连接成功
            
        Raises:
            IMAPConnectionError: 连接失败
            
        Examples:
            >>> client = IMAPClient(config)
            >>> client.connect()
            True
        """
        with self._lock:
            if self.is_connected:
                self.logger.warning("IMAP连接已存在,跳过重复连接")
                return True
            
            try:
                imap_config = self.config.get_imap_config()
                host = imap_config['host']
                port = imap_config['port']
                use_ssl = imap_config['use_ssl']
                timeout = imap_config.get('timeout', 30)
                
                self.logger.info(f"正在连接到IMAP服务器: {host}:{port} (SSL: {use_ssl})")
                
                if use_ssl:
                    self.imap = imaplib.IMAP4_SSL(
                        host=host,
                        port=port,
                        timeout=timeout
                    )
                else:
                    self.imap = imaplib.IMAP4(
                        host=host,
                        port=port
                    )
                    if hasattr(self.imap, 'sock'):
                        self.imap.sock.settimeout(timeout)
                
                self.is_connected = True
                self.logger.info(f"成功连接到IMAP服务器: {host}:{port}")
                return True
                
            except socket.timeout as e:
                error_msg = f"连接IMAP服务器超时: {e}"
                self.logger.error(error_msg)
                raise IMAPConnectionError(error_msg)
            
            except socket.error as e:
                error_msg = f"网络连接失败: {e}"
                self.logger.error(error_msg)
                raise IMAPConnectionError(error_msg)
            
            except Exception as e:
                error_msg = f"连接IMAP服务器时发生未知错误: {e}"
                self.logger.error(error_msg)
                raise IMAPConnectionError(error_msg)
    
    def login(self, email: str, password: str) -> bool:
        """
        登录邮箱
        
        使用账号密码进行IMAP认证。
        
        Args:
            email: 邮箱账号
            password: 邮箱密码
            
        Returns:
            True 如果登录成功
            
        Raises:
            IMAPAuthenticationError: 认证失败
            IMAPConnectionError: 未连接到服务器
            
        Examples:
            >>> client.login("user@gmail.com", "password")
            True
        """
        with self._lock:
            if not self.is_connected or self.imap is None:
                raise IMAPConnectionError("未连接到IMAP服务器,请先调用connect()")
            
            if self.is_authenticated:
                self.logger.warning("已经登录,跳过重复登录")
                return True
            
            try:
                self.logger.info(f"正在登录邮箱: {email}")
                
                # 执行登录
                status, response = self.imap.login(email, password)
                
                if status != 'OK':
                    error_msg = f"登录失败: {response}"
                    self.logger.error(error_msg)
                    raise IMAPAuthenticationError(error_msg)
                
                self.is_authenticated = True
                self.logger.info(f"成功登录邮箱: {email}")
                return True
                
            except imaplib.IMAP4.error as e:
                error_msg = f"IMAP认证失败: {e}"
                self.logger.error(error_msg)
                raise IMAPAuthenticationError(error_msg)
            
            except Exception as e:
                error_msg = f"登录时发生未知错误: {e}"
                self.logger.error(error_msg)
                raise IMAPAuthenticationError(error_msg)
    
    def logout(self) -> None:
        """
        退出登录
        
        安全退出IMAP会话。
        
        Examples:
            >>> client.logout()
        """
        with self._lock:
            if self.imap and self.is_authenticated:
                try:
                    self.imap.logout()
                    self.logger.info("已退出登录")
                except Exception as e:
                    self.logger.warning(f"退出登录时发生错误: {e}")
                finally:
                    self.is_authenticated = False
    
    def disconnect(self) -> None:
        """
        关闭IMAP连接
        
        安全关闭与服务器的连接,释放资源。
        
        Examples:
            >>> client.disconnect()
        """
        with self._lock:
            if self.imap:
                try:
                    if self.is_authenticated:
                        self.logout()
                    
                    self.imap.close()
                    self.logger.info("IMAP连接已关闭")
                except Exception as e:
                    self.logger.warning(f"关闭连接时发生错误: {e}")
                finally:
                    self.imap = None
                    self.is_connected = False
                    self.current_folder = None
    
    # ==================== 文件夹操作 ====================
    
    def list_folders(self) -> List[str]:
        """
        列出所有可用的邮箱文件夹
        
        Returns:
            文件夹名称列表
            
        Raises:
            IMAPOperationError: 操作失败
            
        Examples:
            >>> folders = client.list_folders()
            >>> print(folders)
            ['INBOX', 'Sent', 'Drafts', 'Trash']
        """
        self._ensure_connected()
        
        try:
            status, folder_list = self.imap.list()
            
            if status != 'OK':
                raise IMAPOperationError(f"获取文件夹列表失败: {folder_list}")
            
            folders = []
            for item in folder_list:
                # 解析文件夹名称
                # 格式: b'(\\HasNoChildren) "/" "INBOX"'
                if isinstance(item, bytes):
                    item = item.decode('utf-8')
                
                # 提取文件夹名称
                parts = item.split('"')
                if len(parts) >= 3:
                    folder_name = parts[-2]
                    folders.append(folder_name)
            
            self.logger.debug(f"获取到 {len(folders)} 个文件夹")
            return folders
            
        except Exception as e:
            error_msg = f"获取文件夹列表失败: {e}"
            self.logger.error(error_msg)
            raise IMAPOperationError(error_msg)
    
    def select_folder(self, folder_name: str = "INBOX") -> Dict[str, Any]:
        """
        选择要操作的文件夹
        
        Args:
            folder_name: 文件夹名称(默认: INBOX)
            
        Returns:
            文件夹状态信息字典
            
        Raises:
            IMAPOperationError: 操作失败
            
        Examples:
            >>> status = client.select_folder("INBOX")
            >>> print(status['total_messages'])
            150
        """
        self._ensure_connected()
        
        try:
            self.logger.debug(f"正在选择文件夹: {folder_name}")
            
            status, data = self.imap.select(folder_name)
            
            if status != 'OK':
                raise IMAPOperationError(f"选择文件夹失败: {data}")
            
            self.current_folder = folder_name
            
            # 解析邮件总数
            total_messages = int(data[0].decode('utf-8'))
            
            self.logger.info(f"已选择文件夹: {folder_name}, 共 {total_messages} 封邮件")
            
            return {
                'folder': folder_name,
                'total_messages': total_messages
            }
            
        except Exception as e:
            error_msg = f"选择文件夹 {folder_name} 失败: {e}"
            self.logger.error(error_msg)
            raise IMAPOperationError(error_msg)
    
    def get_folder_status(self, folder_name: str) -> Dict[str, int]:
        """
        获取文件夹状态信息
        
        Args:
            folder_name: 文件夹名称
            
        Returns:
            状态信息字典,包含:
            - messages: 总邮件数
            - recent: 最近邮件数
            - unseen: 未读邮件数
            
        Raises:
            IMAPOperationError: 操作失败
            
        Examples:
            >>> status = client.get_folder_status("INBOX")
            >>> print(f"未读: {status['unseen']}")
            未读: 5
        """
        self._ensure_connected()
        
        try:
            status, data = self.imap.status(
                folder_name, 
                '(MESSAGES RECENT UNSEEN)'
            )
            
            if status != 'OK':
                raise IMAPOperationError(f"获取文件夹状态失败: {data}")
            
            # 解析状态信息
            # 格式: b'"INBOX" (MESSAGES 150 RECENT 0 UNSEEN 5)'
            status_str = data[0].decode('utf-8')
            
            result = {}
            if 'MESSAGES' in status_str:
                result['messages'] = int(status_str.split('MESSAGES')[1].split()[0])
            if 'RECENT' in status_str:
                result['recent'] = int(status_str.split('RECENT')[1].split()[0])
            if 'UNSEEN' in status_str:
                result['unseen'] = int(status_str.split('UNSEEN')[1].split()[0])
            
            self.logger.debug(f"文件夹 {folder_name} 状态: {result}")
            return result
            
        except Exception as e:
            error_msg = f"获取文件夹 {folder_name} 状态失败: {e}"
            self.logger.error(error_msg)
            raise IMAPOperationError(error_msg)
    
    # ==================== 邮件搜索 ====================
    
    @log_performance
    def search_messages(
        self,
        folder: str = "INBOX",
        criteria: str = "ALL",
        limit: Optional[int] = None
    ) -> List[int]:
        """
        搜索邮件,返回UID列表
        
        Args:
            folder: 邮箱文件夹(默认: INBOX)
            criteria: IMAP搜索条件(默认: ALL)
            limit: 限制返回数量(可选)
            
        Returns:
            邮件UID列表
            
        Raises:
            IMAPOperationError: 搜索失败
            
        Examples:
            >>> # 搜索所有邮件
            >>> uids = client.search_messages()
            
            >>> # 搜索未读邮件
            >>> uids = client.search_messages(criteria="UNSEEN")
            
            >>> # 按日期范围搜索
            >>> uids = client.search_messages(
            ...     criteria='SINCE "01-Jan-2024" BEFORE "31-Jan-2024"'
            ... )
        """
        self._ensure_connected()
        
        try:
            # 选择文件夹
            self.select_folder(folder)
            
            self.logger.info(f"正在搜索邮件 - 文件夹: {folder}, 条件: {criteria}")
            
            # 使用UID搜索
            # 使用UID搜索,根据AGENTS.md的规则,不要在criteria前加'ALL'前缀
            if criteria == 'ALL':
                status, data = self.imap.uid('search', None, 'ALL')
            else:
                status, data = self.imap.uid('search', None, criteria)
            
            if status != 'OK':
                raise IMAPOperationError(f"搜索邮件失败: {data}")
            
            # 解析UID列表
            uid_str = data[0].decode('utf-8')
            if not uid_str:
                self.logger.info("未找到符合条件的邮件")
                return []
            
            uids = [int(uid) for uid in uid_str.split()]
            
            # 应用限制
            if limit and limit > 0:
                uids = uids[-limit:]  # 获取最新的N封
            
            self.logger.info(f"找到 {len(uids)} 封符合条件的邮件")
            return uids
            
        except Exception as e:
            error_msg = f"搜索邮件失败: {e}"
            self.logger.error(error_msg)
            raise IMAPOperationError(error_msg)
    
    def get_unseen_messages(self, folder: str = "INBOX") -> List[int]:
        """
        获取所有未读邮件的UID
        
        Args:
            folder: 邮箱文件夹
            
        Returns:
            未读邮件UID列表
            
        Examples:
            >>> unseen_uids = client.get_unseen_messages()
        """
        return self.search_messages(folder=folder, criteria="UNSEEN")
    
    def get_messages_by_date(
        self,
        since_date: Optional[str] = None,
        before_date: Optional[str] = None,
        folder: str = "INBOX"
    ) -> List[int]:
        """
        按日期范围搜索邮件
        
        Args:
            since_date: 起始日期(格式: DD-Mon-YYYY,如 01-Jan-2024)
            before_date: 结束日期(格式: DD-Mon-YYYY)
            folder: 邮箱文件夹
            
        Returns:
            邮件UID列表
            
        Examples:
            >>> uids = client.get_messages_by_date(
            ...     since_date="01-Jan-2024",
            ...     before_date="31-Jan-2024"
            ... )
        """
        criteria_parts = []
        
        if since_date:
            criteria_parts.append(f'SINCE "{since_date}"')
        
        if before_date:
            criteria_parts.append(f'BEFORE "{before_date}"')
        
        criteria = ' '.join(criteria_parts) if criteria_parts else "ALL"
        
        return self.search_messages(folder=folder, criteria=criteria)
    
    def get_latest_messages(
        self,
        limit: int = 10,
        folder: str = "INBOX"
    ) -> List[int]:
        """
        获取最新的N封邮件
        
        Args:
            limit: 邮件数量
            folder: 邮箱文件夹
            
        Returns:
            邮件UID列表(按时间倒序)
            
        Examples:
            >>> latest_uids = client.get_latest_messages(limit=50)
        """
        return self.search_messages(folder=folder, criteria="ALL", limit=limit)
    
    # ==================== 邮件获取 ====================
    
    def fetch_message_by_uid(self, uid: int) -> bytes:
        """
        根据UID获取单封邮件的原始数据
        
        Args:
            uid: 邮件UID
            
        Returns:
            邮件原始数据(bytes)
            
        Raises:
            IMAPOperationError: 获取失败
            
        Examples:
            >>> raw_email = client.fetch_message_by_uid(12345)
        """
        self._ensure_connected()
        
        try:
            self.logger.debug(f"正在获取邮件 UID: {uid}")
            
            # 使用UID FETCH获取完整邮件
            status, data = self.imap.uid('fetch', str(uid), '(RFC822)')
            
            if status != 'OK':
                raise IMAPOperationError(f"获取邮件失败 UID {uid}: {data}")
            
            if not data or not data[0]:
                raise IMAPOperationError(f"邮件 UID {uid} 不存在或已被删除")
            
            # 提取邮件数据
            raw_email = data[0][1]
            
            self.logger.debug(f"成功获取邮件 UID: {uid}, 大小: {len(raw_email)} bytes")
            return raw_email
            
        except Exception as e:
            error_msg = f"获取邮件 UID {uid} 失败: {e}"
            self.logger.error(error_msg)
            raise IMAPOperationError(error_msg)
    
    @log_performance
    def fetch_messages_batch(
        self,
        uids: List[int],
        batch_size: int = 50
    ) -> Generator[Tuple[int, bytes], None, None]:
        """
        批量获取邮件(生成器模式,节省内存)
        
        Args:
            uids: 邮件UID列表
            batch_size: 批次大小(默认50)
            
        Yields:
            (uid, raw_email) 元组
            
        Examples:
            >>> uids = client.search_messages()
            >>> for uid, raw_email in client.fetch_messages_batch(uids):
            ...     # 处理邮件
            ...     pass
        """
        self._ensure_connected()
        
        total = len(uids)
        self.logger.info(f"开始批量获取 {total} 封邮件,批次大小: {batch_size}")
        
        for i in range(0, total, batch_size):
            batch_uids = uids[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size
            
            self.logger.debug(f"处理批次 {batch_num}/{total_batches}: {len(batch_uids)} 封邮件")
            
            for uid in batch_uids:
                try:
                    raw_email = self.fetch_message_by_uid(uid)
                    yield (uid, raw_email)
                except Exception as e:
                    self.logger.error(f"获取邮件 UID {uid} 失败: {e}, 跳过")
                    continue
        
        self.logger.info(f"批量获取完成,共处理 {total} 封邮件")
    
    # ==================== 邮件状态管理 ====================
    
    def mark_as_read(self, uids: List[int]) -> None:
        """
        标记邮件为已读
        
        Args:
            uids: 邮件UID列表
            
        Raises:
            IMAPOperationError: 操作失败
            
        Examples:
            >>> client.mark_as_read([123, 456, 789])
        """
        self._ensure_connected()
        
        try:
            uid_str = ','.join(str(uid) for uid in uids)
            status, data = self.imap.uid('store', uid_str, '+FLAGS', '(\\Seen)')
            
            if status != 'OK':
                raise IMAPOperationError(f"标记邮件为已读失败: {data}")
            
            self.logger.info(f"成功标记 {len(uids)} 封邮件为已读")
            
        except Exception as e:
            error_msg = f"标记邮件为已读失败: {e}"
            self.logger.error(error_msg)
            raise IMAPOperationError(error_msg)
    
    def mark_as_unread(self, uids: List[int]) -> None:
        """
        标记邮件为未读
        
        Args:
            uids: 邮件UID列表
            
        Raises:
            IMAPOperationError: 操作失败
            
        Examples:
            >>> client.mark_as_unread([123, 456])
        """
        self._ensure_connected()
        
        try:
            uid_str = ','.join(str(uid) for uid in uids)
            status, data = self.imap.uid('store', uid_str, '-FLAGS', '(\\Seen)')
            
            if status != 'OK':
                raise IMAPOperationError(f"标记邮件为未读失败: {data}")
            
            self.logger.info(f"成功标记 {len(uids)} 封邮件为未读")
            
        except Exception as e:
            error_msg = f"标记邮件为未读失败: {e}"
            self.logger.error(error_msg)
            raise IMAPOperationError(error_msg)
    
    def delete_messages(self, uids: List[int]) -> None:
        """
        删除邮件(标记为删除)
        
        Args:
            uids: 邮件UID列表
            
        Raises:
            IMAPOperationError: 操作失败
            
        Note:
            邮件只是被标记为删除,需要调用expunge()永久删除
            
        Examples:
            >>> client.delete_messages([123, 456])
            >>> client.expunge()  # 永久删除
        """
        self._ensure_connected()
        
        try:
            uid_str = ','.join(str(uid) for uid in uids)
            status, data = self.imap.uid('store', uid_str, '+FLAGS', '(\\Deleted)')
            
            if status != 'OK':
                raise IMAPOperationError(f"删除邮件失败: {data}")
            
            self.logger.info(f"成功标记 {len(uids)} 封邮件为删除")
            
        except Exception as e:
            error_msg = f"删除邮件失败: {e}"
            self.logger.error(error_msg)
            raise IMAPOperationError(error_msg)
    
    def expunge(self) -> None:
        """
        永久删除已标记删除的邮件
        
        Raises:
            IMAPOperationError: 操作失败
            
        Examples:
            >>> client.expunge()
        """
        self._ensure_connected()
        
        try:
            status, data = self.imap.expunge()
            
            if status != 'OK':
                raise IMAPOperationError(f"永久删除邮件失败: {data}")
            
            self.logger.info("已永久删除标记为删除的邮件")
            
        except Exception as e:
            error_msg = f"永久删除邮件失败: {e}"
            self.logger.error(error_msg)
            raise IMAPOperationError(error_msg)
    
    # ==================== 辅助方法 ====================
    
    def _ensure_connected(self) -> None:
        """
        确保客户端已连接和已认证
        
        Raises:
            IMAPConnectionError: 未连接或未认证
        """
        if not self.is_connected or self.imap is None:
            raise IMAPConnectionError("未连接到IMAP服务器,请先调用connect()")
        
        if not self.is_authenticated:
            raise IMAPAuthenticationError("未登录,请先调用login()")
    
    # ==================== 上下文管理器 ====================
    
    def __enter__(self):
        """
        上下文管理器入口
        
        Examples:
            >>> with IMAPClient(config) as client:
            ...     client.connect()
            ...     # 使用client
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口,自动清理资源
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常traceback
        """
        self.disconnect()
        
        if exc_type:
            self.logger.error(f"上下文退出时发生异常: {exc_val}")
        
        return False  # 不抑制异常
    
    def __repr__(self) -> str:
        """字符串表示"""
        status = "已连接" if self.is_connected else "未连接"
        auth = "已认证" if self.is_authenticated else "未认证"
        return f"<IMAPClient {status}, {auth}, folder={self.current_folder}>"