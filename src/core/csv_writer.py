"""
CSV写入器模块

职责:
- 创建和管理CSV文件
- 写入邮件数据到CSV
- 处理数据格式化和特殊字符转义
- 支持批量写入和增量写入
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from src.models.email_message import EmailMessage
from src.utils.config_manager import ConfigManager
from src.utils.logger import get_logger, log_performance


class CSVWriteError(Exception):
    """CSV写入异常"""
    pass


class CSVWriter:
    """
    CSV写入器类
    
    负责将邮件数据写入CSV文件,支持批量操作和进度追踪。
    
    Attributes:
        output_path: CSV文件完整路径
        config: 配置管理器
        logger: 日志记录器
        file: 文件句柄
        csv_writer: CSV DictWriter实例
        write_count: 已写入邮件数量
        
    Examples:
        # 基本用法
        >>> with CSVWriter('output.csv') as writer:
        ...     writer.write_message(email_message)
        
        # 批量写入
        >>> writer = CSVWriter()
        >>> writer.open()
        >>> writer.write_messages(email_list)
        >>> writer.close()
    """
    
    # CSV字段顺序(与EmailMessage.to_csv_row()输出对应)
    FIELDNAMES = [
        'email_account',
        'message_id',
        'thread_id',
        'subject',
        'date',
        'from',
        'to',
        'cc',
        'body_text',
        'has_attachment',
        'attachment_names',
        'attachment_paths',
        'attachment_count',
        'labels'
    ]
    
    def __init__(
        self,
        output_path: Optional[str] = None,
        config_manager: Optional[ConfigManager] = None,
        logger=None
    ):
        """
        初始化CSV写入器
        
        Args:
            output_path: CSV输出文件路径(可选,从配置读取)
            config_manager: 配置管理器(可选)
            logger: 日志记录器(可选)
        """
        self.config = config_manager
        self.logger = logger or get_logger(__name__)
        
        # 确定输出路径
        if output_path:
            self.output_path = Path(output_path)
        elif config_manager:
            output_config = config_manager.get_output_config()
            output_dir = Path(output_config.get('csv_dir', 'output'))
            filename = output_config.get('csv_filename') or self._generate_filename()
            self.output_path = output_dir / filename
        else:
            self.output_path = Path('output') / self._generate_filename()
        
        # 确保输出目录存在
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 文件句柄和写入器
        self.file = None
        self.csv_writer = None
        self.write_count = 0
        self._is_open = False
        
        self.logger.debug(f"CSV写入器已初始化: {self.output_path}")
    
    def _generate_filename(self) -> str:
        """
        生成默认文件名
        
        Returns:
            格式为 'emails_YYYYMMDD_HHMMSS.csv' 的文件名
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'emails_{timestamp}.csv'
    
    def open(self, append: bool = False) -> None:
        """
        打开CSV文件准备写入
        
        Args:
            append: 是否追加模式(默认False,覆盖写入)
            
        Raises:
            CSVWriteError: 文件打开失败
        """
        if self._is_open:
            self.logger.warning("CSV文件已经打开,跳过重复打开操作")
            return
        
        mode = 'a' if append else 'w'
        
        try:
            # 使用 utf-8-sig 编码(带BOM),确保Excel正确显示中文
            self.file = open(
                self.output_path,
                mode,
                newline='',
                encoding='utf-8-sig'
            )
            
            self.csv_writer = csv.DictWriter(
                self.file,
                fieldnames=self.FIELDNAMES,
                extrasaction='ignore'  # 忽略额外字段
            )
            
            # 标记文件已打开
            self._is_open = True
            
            # 如果是新文件或覆盖模式,写入头部
            if not append or self.output_path.stat().st_size == 0:
                self.write_headers()
            self.logger.info(
                f"CSV文件已打开: {self.output_path} "
                f"(模式: {'追加' if append else '覆盖'})"
            )
            
        except PermissionError as e:
            raise CSVWriteError(f"没有写入权限: {self.output_path}") from e
        except OSError as e:
            raise CSVWriteError(f"打开CSV文件失败: {e}") from e
        except Exception as e:
            raise CSVWriteError(f"未知错误: {e}") from e
    
    def write_headers(self) -> None:
        """
        写入CSV表头
        
        Raises:
            CSVWriteError: 写入失败
        """
        if not self._is_open:
            raise CSVWriteError("文件未打开,请先调用open()方法")
        
        try:
            self.csv_writer.writeheader()
            self.logger.debug("CSV表头已写入")
        except Exception as e:
            raise CSVWriteError(f"写入CSV表头失败: {e}") from e
    
    @log_performance
    def write_message(self, email_message: EmailMessage) -> None:
        """
        写入单封邮件
        
        Args:
            email_message: EmailMessage对象
            
        Raises:
            CSVWriteError: 写入失败
            TypeError: 参数类型错误
        """
        if not isinstance(email_message, EmailMessage):
            raise TypeError("参数必须是EmailMessage对象")
        
        if not self._is_open:
            raise CSVWriteError("文件未打开,请先调用open()方法")
        
        try:
            # 获取CSV行数据
            row = email_message.to_csv_row()
            
            # 清理和验证数据
            row = self._sanitize_row(row)
            
            # 写入行
            self.csv_writer.writerow(row)
            self.write_count += 1
            
            self.logger.debug(
                f"邮件已写入 [{self.write_count}]: "
                f"{email_message.message_id}"
            )
            
        except Exception as e:
            self.logger.error(
                f"写入邮件失败: {email_message.message_id}, "
                f"错误: {e}"
            )
            raise CSVWriteError(f"写入邮件失败: {e}") from e
    
    @log_performance
    def write_messages(self, email_messages: List[EmailMessage]) -> int:
        """
        批量写入邮件
        
        Args:
            email_messages: EmailMessage对象列表
            
        Returns:
            成功写入的邮件数量
            
        Raises:
            CSVWriteError: 写入失败
            TypeError: 参数类型错误
        """
        if not isinstance(email_messages, list):
            raise TypeError("参数必须是EmailMessage对象列表")
        
        if not self._is_open:
            raise CSVWriteError("文件未打开,请先调用open()方法")
        
        success_count = 0
        error_count = 0
        
        self.logger.info(f"开始批量写入 {len(email_messages)} 封邮件")
        
        for i, email_message in enumerate(email_messages, 1):
            try:
                self.write_message(email_message)
                success_count += 1
                
                # 每100封邮件刷新一次缓冲区
                if i % 100 == 0:
                    self.flush()
                    self.logger.info(f"进度: {i}/{len(email_messages)}")
                    
            except Exception as e:
                error_count += 1
                self.logger.error(
                    f"批量写入失败 [{i}/{len(email_messages)}]: {e}"
                )
        
        # 最后刷新一次
        self.flush()
        
        self.logger.info(
            f"批量写入完成: 成功 {success_count}, 失败 {error_count}"
        )
        
        return success_count
    
    def _sanitize_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理CSV行数据
        
        处理None值、特殊字符等
        
        Args:
            row: 原始行数据
            
        Returns:
            清理后的行数据
        """
        sanitized = {}
        
        for key, value in row.items():
            if value is None:
                sanitized[key] = ''
            elif isinstance(value, str):
                # 移除可能导致CSV解析问题的字符
                # CSV库会自动处理引号和逗号的转义
                sanitized[key] = value
            else:
                sanitized[key] = str(value)
        
        return sanitized
    
    def flush(self) -> None:
        """
        强制写入缓冲区内容到磁盘
        
        Raises:
            CSVWriteError: 刷新失败
        """
        if not self._is_open:
            return
        
        try:
            if self.file:
                self.file.flush()
                self.logger.debug("缓冲区已刷新")
        except Exception as e:
            raise CSVWriteError(f"刷新缓冲区失败: {e}") from e
    
    def close(self) -> None:
        """
        关闭CSV文件
        
        确保所有数据写入磁盘并释放资源。
        """
        if not self._is_open:
            return
        
        try:
            if self.file:
                self.flush()
                self.file.close()
                self.file = None
                self.csv_writer = None
                self._is_open = False
                
                self.logger.info(
                    f"CSV文件已关闭: {self.output_path}, "
                    f"共写入 {self.write_count} 封邮件"
                )
        except Exception as e:
            self.logger.error(f"关闭CSV文件时出错: {e}")
    
    def __enter__(self):
        """
        上下文管理器入口
        
        Returns:
            CSVWriter实例
        """
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口
        
        确保文件正确关闭,即使发生异常。
        """
        self.close()
        
        # 不抑制异常
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取写入统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'output_path': str(self.output_path),
            'write_count': self.write_count,
            'is_open': self._is_open,
            'file_size': self.output_path.stat().st_size if self.output_path.exists() else 0
        }
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"CSVWriter(path='{self.output_path}', "
            f"written={self.write_count}, "
            f"open={self._is_open})"
        )


@contextmanager
def create_csv_writer(
    output_path: Optional[str] = None,
    config_manager: Optional[ConfigManager] = None
):
    """
    创建CSV写入器的上下文管理器工厂函数
    
    Args:
        output_path: CSV输出文件路径
        config_manager: 配置管理器
        
    Yields:
        CSVWriter实例
        
    Examples:
        >>> with create_csv_writer('output.csv') as writer:
        ...     writer.write_messages(emails)
    """
    writer = CSVWriter(output_path, config_manager)
    try:
        writer.open()
        yield writer
    finally:
        writer.close()