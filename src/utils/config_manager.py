"""
配置管理器模块

职责:
- 从 .env 文件加载所有配置(包括IMAP服务器、筛选、输出、日志等)
- 支持命令行参数覆盖配置
- 实现配置优先级: 命令行 > 环境变量 > 默认值
- 提供配置验证功能
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from dotenv import load_dotenv


class ConfigError(Exception):
    """配置相关错误"""
    pass


class ConfigManager:
    """
    配置管理器类
    
    单例模式,确保配置在整个应用中只加载一次。
    仅从 .env 文件和命令行参数加载配置。
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        env_path: Optional[str] = None,
        cli_args: Optional[Dict[str, Any]] = None
    ):
        """
        初始化配置管理器
        
        Args:
            env_path: 环境变量文件路径,默认为 .env
            cli_args: 命令行参数字典
        """
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.project_root = Path(__file__).parent.parent.parent
        self.env_path = env_path or self.project_root / '.env'
        self.cli_args = cli_args or {}
        
        # 环境变量存储
        self.env_vars: Dict[str, str] = {}
        
        # 默认配置
        self._defaults = {
            # IMAP配置
            'IMAP_HOST': 'imap.gmail.com',
            'IMAP_PORT': '993',
            'IMAP_USE_SSL': 'true',
            'IMAP_TIMEOUT': '30',
            
            # 邮件配置
            'EMAIL_FOLDER': 'INBOX',
            'EMAIL_MARK_AS_READ': 'false',
            'EMAIL_BATCH_SIZE': '50',
            
            # 筛选配置
            'FILTER_ENABLED': 'true',
            'FILTER_DEFAULT_LIMIT': '1000',
            
            # 输出配置
            'OUTPUT_CSV_DIR': 'output/csv',
            'OUTPUT_CSV_FILENAME': '',  # 空字符串表示使用时间戳
            'OUTPUT_ATTACHMENT_DIR': 'output/attachments',
            'OUTPUT_SAVE_ATTACHMENTS': 'true',
            
            # 日志配置
            'LOG_LEVEL': 'INFO',
            'LOG_FORMAT': '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
            'LOG_FILE': 'logs/app.log'
        }
        
        # 加载配置
        self._load_env()
    
    def _load_env(self):
        """
        加载环境变量
        
        从 .env 文件和系统环境变量中加载配置。
        """
        # 加载 .env 文件
        if os.path.exists(self.env_path):
            load_dotenv(self.env_path, override=True)
        
        # 读取所有相关环境变量
        env_keys = [
            # 认证信息
            'EMAIL_ACCOUNT',
            'EMAIL_PASSWORD',
            
            # IMAP配置
            'IMAP_HOST',
            'IMAP_PORT',
            'IMAP_USE_SSL',
            'IMAP_TIMEOUT',
            
            # 邮件配置
            'EMAIL_FOLDER',
            'EMAIL_MARK_AS_READ',
            'EMAIL_BATCH_SIZE',
            
            # 筛选配置
            'FILTER_ENABLED',
            'FILTER_DEFAULT_LIMIT',
            
            # 输出配置
            'OUTPUT_CSV_DIR',
            'OUTPUT_CSV_FILENAME',
            'OUTPUT_ATTACHMENT_DIR',
            'OUTPUT_SAVE_ATTACHMENTS',
            
            # 日志配置
            'LOG_LEVEL',
            'LOG_FORMAT',
            'LOG_FILE'
        ]
        
        for key in env_keys:
            value = os.getenv(key)
            if value is not None:
                self.env_vars[key] = value
    
    def get(
        self,
        key: str,
        default: Any = None,
        value_type: type = str
    ) -> Any:
        """
        获取配置值
        
        优先级: 命令行参数 > 环境变量 > 默认值
        
        Args:
            key: 配置键名称(环境变量格式,如 'IMAP_HOST')
            default: 默认值
            value_type: 值类型(用于类型转换)
        
        Returns:
            配置值
        """
        # 1. 检查命令行参数
        cli_key = key.lower().replace('_', '-')
        if cli_key in self.cli_args:
            return self._convert_type(self.cli_args[cli_key], value_type)
        
        # 2. 检查环境变量
        if key in self.env_vars:
            return self._convert_type(self.env_vars[key], value_type)
        
        # 3. 使用默认值
        if default is not None:
            return default
        
        # 4. 尝试从 _defaults 获取
        if key in self._defaults:
            return self._convert_type(self._defaults[key], value_type)
        
        return None
    
    def _convert_type(self, value: Any, value_type: type) -> Any:
        """
        类型转换
        
        Args:
            value: 原始值
            value_type: 目标类型
        
        Returns:
            转换后的值
        """
        if value is None:
            return None
        
        if value_type == bool:
            if isinstance(value, bool):
                return value
            return str(value).lower() in ('true', 'yes', '1', 'on')
        
        if value_type == int:
            return int(value)
        
        if value_type == float:
            return float(value)
        
        return str(value)
    
    def get_imap_config(self) -> Dict[str, Any]:
        """
        获取IMAP配置
        
        Returns:
            IMAP配置字典
        """
        return {
            'host': self.get('IMAP_HOST', value_type=str),
            'port': self.get('IMAP_PORT', value_type=int),
            'use_ssl': self.get('IMAP_USE_SSL', value_type=bool),
            'timeout': self.get('IMAP_TIMEOUT', value_type=int)
        }
    
    def get_email_credentials(self) -> Tuple[str, str]:
        """
        获取邮箱认证信息
        
        Returns:
            (邮箱账号, 密码) 元组
        
        Raises:
            ConfigError: 认证信息缺失
        """
        # 优先从命令行参数获取
        email = self.cli_args.get('email') or self.env_vars.get('EMAIL_ACCOUNT')
        password = self.cli_args.get('password') or self.env_vars.get('EMAIL_PASSWORD')
        
        if not email:
            raise ConfigError("邮箱账号未配置。请在 .env 文件中设置 EMAIL_ACCOUNT 或使用 --email 参数")
        
        if not password:
            raise ConfigError("邮箱密码未配置。请在 .env 文件中设置 EMAIL_PASSWORD 或使用 --password 参数")
        
        return email, password
    
    def get_email_config(self) -> Dict[str, Any]:
        """
        获取邮件相关配置
        
        Returns:
            邮件配置字典
        """
        return {
            'default_folder': self.get('EMAIL_FOLDER', value_type=str),
            'mark_as_read': self.get('EMAIL_MARK_AS_READ', value_type=bool),
            'batch_size': self.get('EMAIL_BATCH_SIZE', value_type=int)
        }
    
    def get_filter_config(self) -> Dict[str, Any]:
        """
        获取筛选配置
        
        Returns:
            筛选配置字典
        """
        return {
            'enabled': self.get('FILTER_ENABLED', value_type=bool),
            'default_limit': self.get('FILTER_DEFAULT_LIMIT', value_type=int),
            'from_date': self.cli_args.get('from-date'),
            'to_date': self.cli_args.get('to-date'),
            'sender': self.cli_args.get('sender'),
            'subject': self.cli_args.get('subject'),
            'labels': self.cli_args.get('labels'),
            'limit': self.cli_args.get('limit')
        }
    
    def get_output_config(self) -> Dict[str, Any]:
        """
        获取输出配置
        
        Returns:
            输出配置字典
        """
        csv_dir = self.get('OUTPUT_CSV_DIR', value_type=str)
        attachment_dir = self.get('OUTPUT_ATTACHMENT_DIR', value_type=str)
        
        # 转换为绝对路径
        csv_dir = self._resolve_path(csv_dir)
        attachment_dir = self._resolve_path(attachment_dir)
        
        return {
            'csv_dir': csv_dir,
            'csv_filename': self.get('OUTPUT_CSV_FILENAME', value_type=str) or None,
            'attachment_dir': attachment_dir,
            'save_attachments': self.get('OUTPUT_SAVE_ATTACHMENTS', value_type=bool)
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        获取日志配置
        
        Returns:
            日志配置字典
        """
        log_file = self.get('LOG_FILE', value_type=str)
        log_file = self._resolve_path(log_file)
        
        return {
            'level': self.get('LOG_LEVEL', value_type=str),
            'format': self.get('LOG_FORMAT', value_type=str),
            'file': log_file
        }
    
    def _resolve_path(self, path: str) -> str:
        """
        解析路径为绝对路径
        
        Args:
            path: 相对或绝对路径
        
        Returns:
            绝对路径
        """
        if not path:
            return path
        
        path_obj = Path(path)
        if path_obj.is_absolute():
            return str(path_obj)
        
        return str(self.project_root / path)
    
    def validate(self) -> bool:
        """
        验证配置完整性
        
        检查必需字段、验证数据格式、检查路径有效性等。
        
        Returns:
            True 如果配置有效
        
        Raises:
            ConfigError: 配置验证失败
        """
        errors = []
        
        # 1. 验证邮箱认证信息
        try:
            email, password = self.get_email_credentials()
            
            # 验证邮箱格式
            if not self._is_valid_email(email):
                errors.append(f"邮箱地址格式无效: {email}")
        except ConfigError as e:
            errors.append(str(e))
        
        # 2. 验证IMAP配置
        imap_config = self.get_imap_config()
        
        if not imap_config['host']:
            errors.append("IMAP服务器地址未配置")
        
        port = imap_config['port']
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append(f"IMAP端口无效: {port}")
        
        # 3. 验证输出目录
        output_config = self.get_output_config()
        
        for dir_key in ['csv_dir', 'attachment_dir']:
            dir_path = output_config[dir_key]
            if dir_path:
                # 尝试创建目录
                try:
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"无法创建目录 {dir_path}: {e}")
        
        # 4. 验证日志配置
        logging_config = self.get_logging_config()
        
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if logging_config['level'].upper() not in valid_log_levels:
            errors.append(f"无效的日志级别: {logging_config['level']}")
        
        # 创建日志目录
        log_file = logging_config['file']
        if log_file:
            try:
                Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"无法创建日志目录: {e}")
        
        # 抛出所有错误
        if errors:
            raise ConfigError("配置验证失败:\n" + "\n".join(f"  - {err}" for err in errors))
        
        return True
    
    def _is_valid_email(self, email: str) -> bool:
        """
        验证邮箱地址格式
        
        Args:
            email: 邮箱地址
        
        Returns:
            True 如果格式有效
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def get_all_config(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有配置
        
        Returns:
            完整配置字典
        """
        return {
            'imap': self.get_imap_config(),
            'email': self.get_email_config(),
            'filter': self.get_filter_config(),
            'output': self.get_output_config(),
            'logging': self.get_logging_config()
        }
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"<ConfigManager env_path={self.env_path}>"