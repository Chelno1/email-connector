"""
日志记录系统模块

职责:
- 提供统一的日志记录接口
- 支持控制台和文件双输出
- 从ConfigManager读取日志配置
- 支持日志文件自动轮转
- 为不同模块提供独立的logger实例
- 实现性能监控功能
"""

import logging
import os
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Callable, Any
from functools import wraps

# 尝试导入colorlog以支持彩色日志(可选)
try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False


# 全局变量
_logger_initialized = False
_root_logger = None


class LoggerError(Exception):
    """日志系统相关错误"""
    pass


def setup_logging(config_manager=None) -> None:
    """
    初始化日志系统
    
    根据ConfigManager配置初始化日志系统,包括:
    - 控制台输出处理器
    - 文件输出处理器(支持轮转)
    - 日志格式化
    
    Args:
        config_manager: ConfigManager实例,如果为None则使用默认配置
    
    Raises:
        LoggerError: 日志系统初始化失败
    """
    global _logger_initialized, _root_logger
    
    # 避免重复初始化
    if _logger_initialized:
        return
    
    try:
        # 获取日志配置
        if config_manager:
            log_config = config_manager.get_logging_config()
            log_level = log_config.get('level', 'INFO').upper()
            log_format = log_config.get('format', '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s')
            log_file = log_config.get('file', 'logs/app.log')
        else:
            # 默认配置
            log_level = 'INFO'
            log_format = '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
            log_file = 'logs/app.log'
        
        # 转换日志级别
        numeric_level = _get_log_level(log_level)
        
        # 获取根logger
        root_logger = logging.getLogger('email_connector')
        root_logger.setLevel(numeric_level)
        
        # 清除已有的处理器(避免重复)
        root_logger.handlers.clear()
        
        # 创建时间格式化器
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # 1. 设置控制台处理器
        console_handler = _create_console_handler(log_level, log_format, date_format)
        root_logger.addHandler(console_handler)
        
        # 2. 设置文件处理器
        if log_file:
            file_handler = _create_file_handler(log_file, log_level, log_format, date_format)
            root_logger.addHandler(file_handler)
        
        # 防止日志传播到父logger
        root_logger.propagate = False
        
        # 标记为已初始化
        _logger_initialized = True
        _root_logger = root_logger
        
        # 记录初始化成功
        root_logger.info(f"日志系统初始化成功 - 级别: {log_level}, 文件: {log_file}")
        
    except Exception as e:
        raise LoggerError(f"日志系统初始化失败: {e}")


def _get_log_level(level_name: str) -> int:
    """
    将日志级别字符串转换为logging常量
    
    Args:
        level_name: 日志级别名称
    
    Returns:
        日志级别常量
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    level = level_map.get(level_name.upper())
    if level is None:
        # 默认使用INFO级别
        return logging.INFO
    
    return level


def _create_console_handler(
    log_level: str,
    log_format: str,
    date_format: str
) -> logging.Handler:
    """
    创建控制台处理器
    
    Args:
        log_level: 日志级别
        log_format: 日志格式
        date_format: 时间格式
    
    Returns:
        控制台处理器
    """
    console_handler = logging.StreamHandler()
    console_handler.setLevel(_get_log_level(log_level))
    
    # 如果colorlog可用,使用彩色格式
    if COLORLOG_AVAILABLE:
        color_format = '%(log_color)s' + log_format
        formatter = colorlog.ColoredFormatter(
            color_format,
            datefmt=date_format,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )
    else:
        # 简化的控制台格式(不带文件名和行号)
        simple_format = '[%(asctime)s] [%(levelname)s] %(message)s'
        formatter = logging.Formatter(simple_format, datefmt=date_format)
    
    console_handler.setFormatter(formatter)
    return console_handler


def _create_file_handler(
    log_file: str,
    log_level: str,
    log_format: str,
    date_format: str
) -> logging.Handler:
    """
    创建文件处理器(支持轮转)
    
    Args:
        log_file: 日志文件路径
        log_level: 日志级别
        log_format: 日志格式
        date_format: 时间格式
    
    Returns:
        文件处理器
    """
    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建轮转文件处理器
    # maxBytes: 单个日志文件最大10MB
    # backupCount: 保留最近5个备份文件
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    file_handler.setLevel(_get_log_level(log_level))
    
    # 文件使用更详细的格式
    formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(formatter)
    
    return file_handler


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取logger实例
    
    为指定模块获取独立的logger实例。如果日志系统未初始化,
    将使用默认配置自动初始化。
    
    Args:
        name: logger名称,通常使用 __name__
    
    Returns:
        Logger实例
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("模块初始化成功")
    """
    # 如果未初始化,使用默认配置初始化
    if not _logger_initialized:
        setup_logging()
    
    # 如果没有提供名称,返回根logger
    if name is None:
        if _root_logger is None:
            # 如果根logger未初始化,创建一个基础logger
            return logging.getLogger('email_connector')
        return _root_logger
    
    # 返回子logger
    # 格式: email_connector.module_name
    logger_name = f"email_connector.{name}" if name else "email_connector"
    logger = logging.getLogger(logger_name)
    
    return logger


def log_performance(func: Callable) -> Callable:
    """
    性能监控装饰器
    
    记录函数执行时间,用于性能分析和优化。
    
    Args:
        func: 要监控的函数
    
    Returns:
        包装后的函数
    
    Example:
        >>> @log_performance
        ... def fetch_emails():
        ...     # 邮件获取逻辑
        ...     pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = get_logger(func.__module__)
        
        # 记录开始
        start_time = time.time()
        func_name = func.__qualname__
        logger.debug(f"开始执行: {func_name}")
        
        try:
            # 执行函数
            result = func(*args, **kwargs)
            
            # 记录成功和耗时
            elapsed_time = time.time() - start_time
            logger.info(f"执行完成: {func_name} - 耗时: {elapsed_time:.3f}秒")
            
            return result
            
        except Exception as e:
            # 记录失败和耗时
            elapsed_time = time.time() - start_time
            logger.error(f"执行失败: {func_name} - 耗时: {elapsed_time:.3f}秒 - 错误: {e}")
            raise
    
    return wrapper


def log_function_call(func: Callable) -> Callable:
    """
    函数调用日志装饰器
    
    记录函数的调用信息,包括参数和返回值(用于调试)。
    
    Args:
        func: 要记录的函数
    
    Returns:
        包装后的函数
    
    Example:
        >>> @log_function_call
        ... def process_email(email_id: str):
        ...     pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger = get_logger(func.__module__)
        
        func_name = func.__qualname__
        
        # 记录调用
        logger.debug(f"调用函数: {func_name} - args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数返回: {func_name} - result={result}")
            return result
        except Exception as e:
            logger.error(f"函数异常: {func_name} - error={e}")
            raise
    
    return wrapper


class LogContext:
    """
    日志上下文管理器
    
    用于在代码块中临时改变日志级别或添加上下文信息。
    
    Example:
        >>> with LogContext(logger, level=logging.DEBUG):
        ...     # 在此代码块中使用DEBUG级别
        ...     logger.debug("详细调试信息")
    """
    
    def __init__(
        self,
        logger: logging.Logger,
        level: Optional[int] = None,
        extra: Optional[dict] = None
    ):
        """
        初始化日志上下文
        
        Args:
            logger: Logger实例
            level: 临时日志级别
            extra: 额外的上下文信息
        """
        self.logger = logger
        self.new_level = level
        self.extra = extra or {}
        self.old_level = None
    
    def __enter__(self):
        """进入上下文"""
        if self.new_level is not None:
            self.old_level = self.logger.level
            self.logger.setLevel(self.new_level)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if self.old_level is not None:
            self.logger.setLevel(self.old_level)


def reset_logging() -> None:
    """
    重置日志系统
    
    清除所有处理器和配置,用于测试或重新初始化。
    """
    global _logger_initialized, _root_logger
    
    if _root_logger:
        # 清除所有处理器
        for handler in _root_logger.handlers[:]:
            handler.close()
            _root_logger.removeHandler(handler)
    
    _logger_initialized = False
    _root_logger = None


# 便利函数:直接使用根logger记录日志
def debug(msg: str, *args, **kwargs) -> None:
    """记录DEBUG级别日志"""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """记录INFO级别日志"""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """记录WARNING级别日志"""
    get_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """记录ERROR级别日志"""
    get_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """记录CRITICAL级别日志"""
    get_logger().critical(msg, *args, **kwargs)