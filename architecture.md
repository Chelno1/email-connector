# IMAP邮件提取和CSV导出系统 - 架构设计文档

## 1. 项目概述

### 1.1 项目目标
构建一个专业级的IMAP邮件提取和CSV导出Python程序,支持:
- 多维度邮件筛选(日期范围、发件人、主题关键词、标签)
- 完整的MIME解析和附件处理
- 结构化CSV输出
- 灵活的CLI命令行接口
- 模块化设计,易于扩展

### 1.2 技术栈
- **语言**: Python 3.8+
- **核心库**: 
  - `imaplib`: IMAP协议客户端
  - `email`: MIME解析
  - `csv`: CSV文件操作
  - `configparser`: 配置文件管理
  - `argparse`: CLI参数解析
  - `logging`: 日志系统
  - `python-dotenv`: 环境变量管理
  
### 1.3 性能目标
- 支持千级邮件处理
- 内存优化的流式处理
- 支持批量操作和进度追踪

---

## 2. 项目目录结构

```
email-connector/
│
├── src/                          # 源代码目录
│   ├── __init__.py
│   ├── main.py                   # 主程序入口
│   ├── cli.py                    # CLI命令行接口
│   │
│   ├── core/                     # 核心功能模块
│   │   ├── __init__.py
│   │   ├── imap_client.py        # IMAP客户端
│   │   ├── email_parser.py       # 邮件解析器
│   │   ├── csv_writer.py         # CSV写入器
│   │   └── filter_engine.py      # 邮件筛选引擎
│   │
│   ├── utils/                    # 工具模块
│   │   ├── __init__.py
│   │   ├── config_manager.py     # 配置管理
│   │   ├── logger.py             # 日志系统
│   │   ├── validators.py         # 数据验证
│   │   └── helpers.py            # 辅助函数
│   │
│   └── models/                   # 数据模型
│       ├── __init__.py
│       ├── email_message.py      # 邮件消息模型
│       └── attachment.py         # 附件模型
│
├── config/                       # 配置文件目录
│   ├── config.ini.example        # 配置文件模板
│   └── .env.example              # 环境变量模板
│
├── output/                       # 输出文件目录
│   ├── csv/                      # CSV文件存放
│   └── attachments/              # 附件存放
│       └── YYYY-MM-DD/           # 按日期分类
│
├── logs/                         # 日志文件目录
│   ├── app.log                   # 应用日志
│   └── error.log                 # 错误日志
│
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── test_imap_client.py
│   ├── test_email_parser.py
│   ├── test_csv_writer.py
│   └── test_filter_engine.py
│
├── docs/                         # 文档目录
│   ├── architecture.md           # 架构设计文档(本文件)
│   └── user_guide.md             # 用户指南
│
├── requirements.txt              # 依赖包列表
├── setup.py                      # 安装脚本
├── .gitignore                    # Git忽略文件
└── README.md                     # 项目说明
```

---

## 3. 核心模块设计

### 3.1 main.py - 主程序入口

**职责:**
- 协调各模块的工作流程
- 处理程序的整体逻辑
- 异常处理和资源清理

**主要流程:**
```
1. 解析CLI参数
2. 加载配置
3. 初始化日志系统
4. 创建IMAP客户端连接
5. 应用邮件筛选条件
6. 批量获取并解析邮件
7. 写入CSV文件
8. 处理附件
9. 清理资源
10. 输出统计信息
```

**核心接口:**
```python
def main(args: argparse.Namespace) -> int:
    """
    主程序入口
    
    Args:
        args: CLI参数对象
        
    Returns:
        int: 退出代码(0=成功, 非0=失败)
    """
    pass
```

---

### 3.2 cli.py - 命令行接口

**职责:**
- 定义所有CLI参数
- 参数验证和预处理
- 提供友好的帮助信息

**参数设计:**

| 参数组 | 参数名 | 类型 | 必需 | 默认值 | 说明 |
|--------|--------|------|------|--------|------|
| **连接参数** | --host | str | 否 | config.ini | IMAP服务器地址 |
| | --port | int | 否 | config.ini | IMAP端口 |
| | --email | str | 否 | .env | 邮箱账号 |
| | --password | str | 否 | .env | 邮箱密码 |
| | --use-ssl | bool | 否 | True | 使用SSL连接 |
| **筛选参数** | --folder | str | 否 | INBOX | 邮箱文件夹 |
| | --from-date | str | 否 | None | 起始日期(YYYY-MM-DD) |
| | --to-date | str | 否 | None | 结束日期(YYYY-MM-DD) |
| | --sender | str | 否 | None | 发件人过滤 |
| | --subject | str | 否 | None | 主题关键词 |
| | --labels | str | 否 | None | 标签过滤(逗号分隔) |
| | --limit | int | 否 | None | 最大邮件数量 |
| **输出参数** | --output | str | 否 | output/csv | CSV输出路径 |
| | --filename | str | 否 | emails_{timestamp}.csv | CSV文件名 |
| | --save-attachments | bool | 否 | True | 保存附件 |
| | --attachment-dir | str | 否 | output/attachments | 附件目录 |
| **其他参数** | --config | str | 否 | config/config.ini | 配置文件路径 |
| | --log-level | str | 否 | INFO | 日志级别 |
| | --verbose | bool | 否 | False | 详细输出 |
| | --dry-run | bool | 否 | False | 仅模拟,不实际执行 |

**核心接口:**
```python
def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    pass

def validate_arguments(args: argparse.Namespace) -> bool:
    """验证参数有效性"""
    pass
```

---

### 3.3 core/imap_client.py - IMAP客户端

**职责:**
- 建立和管理IMAP连接
- 提供邮件获取接口
- 处理IMAP协议相关操作
- 连接池管理(可选)

**核心类:**
```python
class IMAPClient:
    """IMAP客户端类"""
    
    def __init__(self, host: str, port: int, use_ssl: bool = True):
        """初始化IMAP客户端"""
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.connection = None
        
    def connect(self) -> bool:
        """建立IMAP连接"""
        pass
        
    def login(self, email: str, password: str) -> bool:
        """登录邮箱"""
        pass
        
    def select_folder(self, folder: str = 'INBOX') -> bool:
        """选择邮箱文件夹"""
        pass
        
    def search(self, criteria: dict) -> list[str]:
        """
        搜索邮件
        
        Args:
            criteria: 搜索条件字典
                {
                    'from_date': '2024-01-01',
                    'to_date': '2024-12-31',
                    'sender': 'example@email.com',
                    'subject': 'keyword',
                    'labels': ['IMPORTANT', 'WORK']
                }
                
        Returns:
            list[str]: 邮件ID列表
        """
        pass
        
    def fetch_email(self, email_id: str) -> bytes:
        """
        获取单封邮件的原始数据
        
        Args:
            email_id: 邮件ID
            
        Returns:
            bytes: 邮件原始数据
        """
        pass
        
    def fetch_emails_batch(self, email_ids: list[str], 
                           batch_size: int = 50) -> Iterator[bytes]:
        """
        批量获取邮件(生成器,节省内存)
        
        Args:
            email_ids: 邮件ID列表
            batch_size: 批次大小
            
        Yields:
            bytes: 邮件原始数据
        """
        pass
        
    def close(self):
        """关闭连接"""
        pass
        
    def __enter__(self):
        """上下文管理器入口"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
```

**错误处理:**
- `IMAPConnectionError`: 连接失败
- `IMAPAuthenticationError`: 认证失败
- `IMAPOperationError`: 操作失败

---

### 3.4 core/email_parser.py - 邮件解析器

**职责:**
- 解析MIME邮件结构
- 提取邮件元数据
- 提取邮件正文(HTML/纯文本)
- 处理附件信息

**核心类:**
```python
class EmailParser:
    """邮件解析器类"""
    
    def __init__(self):
        self.charset_detector = chardet.detect
        
    def parse(self, raw_email: bytes) -> EmailMessage:
        """
        解析邮件
        
        Args:
            raw_email: 邮件原始数据
            
        Returns:
            EmailMessage: 邮件消息对象
        """
        pass
        
    def extract_headers(self, msg: email.message.Message) -> dict:
        """
        提取邮件头信息
        
        Returns:
            {
                'message_id': str,
                'subject': str,
                'from': str,
                'to': list[str],
                'cc': list[str],
                'bcc': list[str],
                'date': datetime,
                'labels': list[str],
                'in_reply_to': str,
                'references': list[str]
            }
        """
        pass
        
    def extract_body(self, msg: email.message.Message) -> dict:
        """
        提取邮件正文
        
        Returns:
            {
                'text_plain': str,
                'text_html': str,
                'charset': str
            }
        """
        pass
        
    def extract_attachments(self, msg: email.message.Message) -> list[Attachment]:
        """
        提取附件信息
        
        Returns:
            list[Attachment]: 附件对象列表
        """
        pass
        
    def decode_header(self, header_value: str) -> str:
        """解码邮件头(处理编码)"""
        pass
        
    def clean_text(self, text: str, max_length: int = None) -> str:
        """清理文本内容"""
        pass
```

---

### 3.5 core/csv_writer.py - CSV写入器

**职责:**
- 创建和管理CSV文件
- 写入邮件数据
- 处理数据格式化
- 支持增量写入

**核心类:**
```python
class CSVWriter:
    """CSV写入器类"""
    
    def __init__(self, output_path: str, filename: str = None):
        """
        初始化CSV写入器
        
        Args:
            output_path: 输出目录
            filename: 文件名(可选,默认使用时间戳)
        """
        self.output_path = output_path
        self.filename = filename or f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.full_path = os.path.join(output_path, self.filename)
        self.file_handle = None
        self.csv_writer = None
        
    def open(self):
        """打开CSV文件"""
        pass
        
    def write_header(self):
        """写入CSV表头"""
        pass
        
    def write_email(self, email_msg: EmailMessage):
        """
        写入单封邮件
        
        Args:
            email_msg: 邮件消息对象
        """
        pass
        
    def write_emails_batch(self, emails: list[EmailMessage]):
        """批量写入邮件"""
        pass
        
    def format_row(self, email_msg: EmailMessage) -> dict:
        """
        格式化邮件数据为CSV行
        
        Returns:
            {
                'message_id': str,
                'subject': str,
                'from': str,
                'to': str,  # 逗号分隔
                'cc': str,
                'date': str,  # ISO格式
                'text_plain': str,
                'text_html': str,
                'attachment_count': int,
                'attachment_names': str,  # 逗号分隔
                'attachment_paths': str,  # 逗号分隔
                'labels': str,
                'size_bytes': int
            }
        """
        pass
        
    def close(self):
        """关闭文件"""
        pass
        
    def __enter__(self):
        """上下文管理器入口"""
        self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
```

---

### 3.6 core/filter_engine.py - 邮件筛选引擎

**职责:**
- 构建IMAP搜索条件
- 提供灵活的筛选规则组合
- 支持复杂查询逻辑

**核心类:**
```python
class FilterEngine:
    """邮件筛选引擎"""
    
    def __init__(self):
        self.criteria = {}
        
    def add_date_range(self, from_date: str, to_date: str):
        """添加日期范围筛选"""
        pass
        
    def add_sender_filter(self, sender: str):
        """添加发件人筛选"""
        pass
        
    def add_subject_filter(self, keyword: str):
        """添加主题关键词筛选"""
        pass
        
    def add_label_filter(self, labels: list[str]):
        """添加标签筛选"""
        pass
        
    def build_imap_search_criteria(self) -> str:
        """
        构建IMAP搜索条件字符串
        
        Returns:
            str: IMAP搜索条件
            例: '(SINCE "01-Jan-2024" BEFORE "31-Dec-2024" FROM "example@email.com")'
        """
        pass
        
    def validate_criteria(self) -> bool:
        """验证筛选条件的有效性"""
        pass
```

---

### 3.7 utils/config_manager.py - 配置管理器

**职责:**
- 加载配置文件
- 管理环境变量
- 提供配置访问接口
- 配置验证

**核心类:**
```python
class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = 'config/config.ini'):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.env_vars = {}
        
    def load_config(self):
        """加载配置文件"""
        pass
        
    def load_env(self, env_path: str = '.env'):
        """加载环境变量"""
        pass
        
    def get(self, section: str, key: str, default=None):
        """获取配置值(优先级: 环境变量 > 配置文件 > 默认值)"""
        pass
        
    def get_imap_config(self) -> dict:
        """获取IMAP配置"""
        pass
        
    def get_output_config(self) -> dict:
        """获取输出配置"""
        pass
        
    def validate(self) -> bool:
        """验证配置完整性"""
        pass
```

---

### 3.8 utils/logger.py - 日志系统

**职责:**
- 配置日志系统
- 提供统一的日志接口
- 支持多级别日志
- 日志文件轮转

**核心功能:**
```python
def setup_logger(
    name: str = 'email_connector',
    log_level: str = 'INFO',
    log_dir: str = 'logs'
) -> logging.Logger:
    """
    设置日志系统
    
    配置:
    - 控制台输出: INFO及以上
    - 文件输出: DEBUG及以上 (app.log)
    - 错误文件: ERROR及以上 (error.log)
    - 日志轮转: 10MB per file, 保留5个备份
    
    Args:
        name: 日志名称
        log_level: 日志级别
        log_dir: 日志目录
        
    Returns:
        logging.Logger: 日志对象
    """
    pass

def get_logger(name: str = None) -> logging.Logger:
    """获取日志对象"""
    pass
```

**日志格式:**
```
[2024-01-15 14:30:25] [INFO] [imap_client.py:45] Successfully connected to imap.gmail.com
[2024-01-15 14:30:26] [DEBUG] [email_parser.py:123] Parsing email ID: 12345
[2024-01-15 14:30:27] [ERROR] [imap_client.py:78] Connection timeout: Connection refused
```

---

### 3.9 models/email_message.py - 邮件消息模型

**职责:**
- 定义邮件数据结构
- 提供数据验证
- 数据序列化

**核心类:**
```python
@dataclass
class EmailMessage:
    """邮件消息数据模型"""
    
    # 元数据
    message_id: str
    subject: str
    sender: str
    recipients: list[str]
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    date: datetime
    
    # 内容
    text_plain: str = ""
    text_html: str = ""
    charset: str = "utf-8"
    
    # 附件
    attachments: list['Attachment'] = field(default_factory=list)
    
    # 其他
    labels: list[str] = field(default_factory=list)
    size_bytes: int = 0
    in_reply_to: str = None
    references: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        pass
        
    def has_attachments(self) -> bool:
        """是否包含附件"""
        return len(self.attachments) > 0
        
    def get_attachment_names(self) -> list[str]:
        """获取所有附件名称"""
        return [att.filename for att in self.attachments]
```

---

### 3.10 models/attachment.py - 附件模型

**职责:**
- 定义附件数据结构
- 提供附件保存接口

**核心类:**
```python
@dataclass
class Attachment:
    """附件数据模型"""
    
    filename: str
    content_type: str
    size_bytes: int
    content: bytes
    saved_path: str = None
    
    def save(self, output_dir: str) -> str:
        """
        保存附件到本地
        
        Args:
            output_dir: 输出目录
            
        Returns:
            str: 保存路径
        """
        pass
        
    def get_extension(self) -> str:
        """获取文件扩展名"""
        return os.path.splitext(self.filename)[1]
        
    def is_image(self) -> bool:
        """是否为图片"""
        return self.content_type.startswith('image/')
        
    def to_dict(self) -> dict:
        """转换为字典(不包含content)"""
        return {
            'filename': self.filename,
            'content_type': self.content_type,
            'size_bytes': self.size_bytes,
            'saved_path': self.saved_path
        }
```

---

## 4. 数据流和模块交互

### 4.1 整体流程图

```
[CLI参数解析] 
    ↓
[配置加载] (ConfigManager)
    ↓
[日志初始化] (Logger)
    ↓
[IMAP连接] (IMAPClient)
    ↓
[邮件筛选] (FilterEngine)
    ↓
[搜索邮件] (IMAPClient.search)
    ↓
[批量获取] (IMAPClient.fetch_emails_batch)
    ↓
┌─────────────────────────┐
│  邮件处理循环 (逐封)      │
│  ┌──────────────────┐   │
│  │ 解析邮件         │   │
│  │ (EmailParser)    │   │
│  └────────┬─────────┘   │
│           ↓             │
│  ┌──────────────────┐   │
│  │ 提取附件         │   │
│  │ (Attachment)     │   │
│  └────────┬─────────┘   │
│           ↓             │
│  ┌──────────────────┐   │
│  │ 保存附件         │   │
│  └────────┬─────────┘   │
│           ↓             │
│  ┌──────────────────┐   │
│  │ 写入CSV          │   │
│  │ (CSVWriter)      │   │
│  └──────────────────┘   │
└─────────────────────────┘
    ↓
[关闭连接] (IMAPClient.close)
    ↓
[输出统计信息]
```

### 4.2 模块依赖关系

```
main.py
  ├─> cli.py
  ├─> utils/config_manager.py
  ├─> utils/logger.py
  ├─> core/imap_client.py
  │     └─> utils/validators.py
  ├─> core/filter_engine.py
  ├─> core/email_parser.py
  │     ├─> models/email_message.py
  │     └─> models/attachment.py
  └─> core/csv_writer.py
        └─> models/email_message.py
```

### 4.3 数据传递接口

**IMAPClient → EmailParser:**
```python
raw_email: bytes → EmailParser.parse() → EmailMessage
```

**EmailParser → CSVWriter:**
```python
EmailMessage → CSVWriter.write_email() → CSV文件
```

**EmailParser → Attachment:**
```python
EmailMessage.attachments → Attachment.save() → 本地文件
```

---

## 5. 配置文件结构

### 5.1 config.ini 结构

```ini
[IMAP]
# IMAP服务器配置
host = imap.gmail.com
port = 993
use_ssl = true
timeout = 30

[FILTER]
# 默认筛选配置
default_folder = INBOX
default_limit = 1000
date_format = %%Y-%%m-%%d

[OUTPUT]
# 输出配置
csv_output_dir = output/csv
attachment_output_dir = output/attachments
csv_encoding = utf-8
csv_delimiter = ,
max_text_length = 10000

[LOGGING]
# 日志配置
log_dir = logs
log_level = INFO
log_format = [%%(asctime)s] [%%(levelname)s] [%%(filename)s:%%(lineno)d] %%(message)s
max_log_size = 10485760
backup_count = 5

[PERFORMANCE]
# 性能配置
batch_size = 50
connection_pool_size = 5
retry_times = 3
retry_delay = 5
```

### 5.2 .env 文件结构

```env
# IMAP认证信息 (敏感信息,不应提交到版本控制)
IMAP_EMAIL=your-email@gmail.com
IMAP_PASSWORD=your-app-password

# 可选:覆盖config.ini中的配置
IMAP_HOST=imap.gmail.com
IMAP_PORT=993

# 日志级别覆盖
LOG_LEVEL=DEBUG
```

### 5.3 配置优先级

```
命令行参数 > 环境变量(.env) > 配置文件(config.ini) > 默认值
```

**示例:**
- 如果同时指定了 `--host`, `.env中的IMAP_HOST`, `config.ini中的host`
- 最终使用 `--host` 的值

---

## 6. CSV输出格式规范

### 6.1 字段定义

| 字段名 | 数据类型 | 格式 | 说明 | 示例 |
|--------|----------|------|------|------|
| message_id | string | - | 邮件唯一标识 | `<abc123@mail.gmail.com>` |
| subject | string | - | 邮件主题 | `Re: Project Update` |
| from | string | - | 发件人(名称 <邮箱>) | `John Doe <john@example.com>` |
| to | string | 逗号分隔 | 收件人列表 | `alice@example.com, bob@example.com` |
| cc | string | 逗号分隔 | 抄送列表 | `charlie@example.com` |
| date | string | ISO 8601 | 邮件日期时间 | `2024-01-15T14:30:25+08:00` |
| text_plain | string | - | 纯文本正文 | `Hello, this is...` |
| text_html | string | - | HTML正文 | `<html><body>...` |
| attachment_count | integer | - | 附件数量 | `3` |
| attachment_names | string | 逗号分隔 | 附件文件名列表 | `report.pdf, image.png` |
| attachment_paths | string | 逗号分隔 | 附件保存路径列表 | `output/attachments/2024-01-15/report.pdf` |
| labels | string | 逗号分隔 | 邮件标签 | `IMPORTANT, WORK` |
| size_bytes | integer | - | 邮件大小(字节) | `15234` |

### 6.2 CSV文件示例

```csv
message_id,subject,from,to,cc,date,text_plain,text_html,attachment_count,attachment_names,attachment_paths,labels,size_bytes
"<abc123@mail.gmail.com>","Project Update","John Doe <john@example.com>","alice@example.com","bob@example.com","2024-01-15T14:30:25+08:00","Please review the attached report...","<html><body><p>Please review...</p></body></html>","1","report.pdf","output/attachments/2024-01-15/report.pdf","IMPORTANT,WORK","15234"
```

### 6.3 数据处理规则

1. **文本字段:**
   - 自动去除首尾空白
   - 转义CSV特殊字符(逗号、引号、换行)
   - 超长文本截断(默认10000字符,可配置)

2. **日期字段:**
   - 统一使用ISO 8601格式
   - 包含时区信息

3. **列表字段:**
   - 使用逗号分隔
   - 整体用引号包裹

4. **编码:**
   - 默认UTF-8
   - 支持BOM(Excel兼容)

---

## 7. CLI使用示例

### 7.1 基础用法

```bash
# 最简单用法(使用默认配置)
python src/main.py

# 指定邮箱账号和密码
python src/main.py --email user@gmail.com --password "your-password"

# 使用配置文件
python src/main.py --config config/my-config.ini
```

### 7.2 筛选示例

```bash
# 按日期范围筛选
python src/main.py --from-date 2024-01-01 --to-date 2024-01-31

# 按发件人筛选
python src/main.py --sender "important-sender@example.com"

# 按主题关键词筛选
python src/main.py --subject "urgent"

# 按标签筛选
python src/main.py --labels "IMPORTANT,WORK"

# 组合筛选
python src/main.py \
  --from-date 2024-01-01 \
  --sender "boss@company.com" \
  --subject "report" \
  --limit 100
```

### 7.3 输出控制

```bash
# 指定输出文件名
python src/main.py --filename my-emails.csv

# 指定输出目录
python src/main.py --output /path/to/output

# 不保存附件
python src/main.py --save-attachments false

# 指定附件目录
python src/main.py --attachment-dir /path/to/attachments
```

### 7.4 高级用法

```bash
# 详细输出模式
python src/main.py --verbose

# 仅模拟(不实际写入文件)
python src/main.py --dry-run

# 调试模式
python src/main.py --log-level DEBUG

# 指定邮箱文件夹
python src/main.py --folder "Sent"

# 完整示例
python src/main.py \
  --host imap.gmail.com \
  --port 993 \
  --email user@gmail.com \
  --from-date 2024-01-01 \
  --to-date 2024-01-31 \
  --sender "important@example.com" \
  --subject "quarterly report" \
  --labels "IMPORTANT" \
  --limit 500 \
  --output ./exports \
  --filename Q1-2024-emails.csv \
  --save-attachments true \
  --attachment-dir ./exports/attachments \
  --log-level INFO \
  --verbose
```

---

## 8. 扩展性设计

### 8.1 支持POP3协议

**设计思路:**
1. 创建抽象基类 `EmailClient`
2. `IMAPClient` 和 `POP3Client` 继承自 `EmailClient`
3. 提供统一接口

**目录结构变化:**
```
src/core/
  ├── email_client.py          # 抽象基类
  ├── imap_client.py           # IMAP实现
  └── pop3_client.py           # POP3实现 (新增)
```

**抽象接口:**
```python
from abc import ABC, abstractmethod

class EmailClient(ABC):
    """邮件客户端抽象基类"""
    
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def login(self, email: str, password: str) -> bool:
        pass
    
    @abstractmethod
    def search(self, criteria: dict) -> list[str]:
        pass
    
    @abstractmethod
    def fetch_email(self, email_id: str) -> bytes:
        pass
```

### 8.2 支持数据库输出

**设计思路:**
1. 创建抽象基类 `OutputWriter`
2. `CSVWriter` 和 `DatabaseWriter` 继承自 `OutputWriter`
3. 支持多种数据库(SQLite, MySQL, PostgreSQL)

**目录结构变化:**
```
src/core/
  ├── output_writer.py         # 抽象基类
  ├── csv_writer.py            # CSV实现
  └── database_writer.py       # 数据库实现 (新增)
```

**数据库表结构:**
```sql
CREATE TABLE emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    subject TEXT,
    sender VARCHAR(255),
    recipients TEXT,
    cc TEXT,
    date TIMESTAMP,
    text_plain TEXT,
    text_html TEXT,
    labels TEXT,
    size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_message_id VARCHAR(255),
    filename VARCHAR(255),
    content_type VARCHAR(100),
    size_bytes INTEGER,
    saved_path TEXT,
    FOREIGN KEY (email_message_id) REFERENCES emails(message_id)
);
```

### 8.3 支持多邮箱账号

**设计思路:**
1. 配置文件支持多账号定义
2. 主程序支持批量处理
3. 输出文件按账号分类

**配置文件示例:**
```ini
[ACCOUNT_1]
email = user1@gmail.com
password = ${ACCOUNT_1_PASSWORD}
host = imap.gmail.com

[ACCOUNT_2]
email = user2@outlook.com
password = ${ACCOUNT_2_PASSWORD}
host = outlook.office365.com
```

### 8.4 支持邮件发送

**设计思路:**
1. 创建 `smtp_client.py` 模块
2. 支持邮件模板
3. 支持批量发送

**目录结构变化:**
```
src/core/
  └── smtp_client.py           # SMTP客户端 (新增)
```

### 8.5 支持Web界面

**设计思路:**
1. 使用Flask/FastAPI构建Web API
2. 前端使用React/Vue
3. 后台任务队列(Celery)

**目录结构变化:**
```
web/
  ├── backend/
  │   ├── app.py
  │   └── api/
  └── frontend/
      ├── src/
      └── public/
```

### 8.6 插件系统设计

**设计思路:**
1. 定义插件接口
2. 支持自定义邮件处理器
3. 支持自定义输出格式

**示例:**
```python
class EmailProcessorPlugin(ABC):
    """邮件处理插件基类"""
    
    @abstractmethod
    def process(self, email: EmailMessage) -> EmailMessage:
        """处理邮件"""
        pass

# 用户自定义插件
class SpamFilterPlugin(EmailProcessorPlugin):
    def process(self, email: EmailMessage) -> EmailMessage:
        # 垃圾邮件过滤逻辑
        if self.is_spam(email):
            email.labels.append('SPAM')
        return email
```

---

## 9. 安全性考虑

### 9.1 认证安全

1. **密码存储:**
   - 使用环境变量,不在代码中硬编码
   - `.env` 文件加入 `.gitignore`
   - 支持密钥管理工具(如keyring)

2. **连接安全:**
   - 默认使用SSL/TLS
   - 验证服务器证书
   - 支持自签名证书(可配置)

3. **未来扩展:**
   - OAuth2认证支持
   - 双因素认证支持

### 9.2 数据安全

1. **敏感信息:**
   - 邮件内容不记录日志
   - 支持数据脱敏选项
   - 附件可选加密存储

2. **文件权限:**
   - 输出文件设置适当权限(600)
   - 日志文件限制访问

### 9.3 错误处理

1. **异常捕获:**
   - 全局异常处理
   - 详细错误日志
   - 用户友好的错误消息

2. **资源清理:**
   - 使用上下文管理器
   - 确保连接正确关闭
   - 临时文件自动清理

---

## 10. 性能优化策略

### 10.1 内存优化

1. **流式处理:**
   - 使用生成器批量获取邮件
   - 边获取边处理,不全部加载到内存

2. **附件处理:**
   - 大附件流式写入
   - 可选跳过大附件

### 10.2 速度优化

1. **批量操作:**
   - IMAP批量fetch
   - CSV批量写入

2. **并发处理:**
   - 多线程/多进程解析邮件
   - 连接池管理

3. **缓存机制:**
   - 邮件ID缓存
   - 重复附件检测

### 10.3 网络优化

1. **连接管理:**
   - 连接池复用
   - 超时重试机制

2. **断点续传:**
   - 记录处理进度
   - 支持从中断处继续

---

## 11. 测试策略

### 11.1 单元测试

**覆盖模块:**
- `test_imap_client.py`: IMAP连接和操作测试
- `test_email_parser.py`: 邮件解析测试
- `test_csv_writer.py`: CSV写入测试
- `test_filter_engine.py`: 筛选引擎测试
- `test_config_manager.py`: 配置管理测试

**工具:**
- `pytest`: 测试框架
- `unittest.mock`: 模拟IMAP服务器
- `pytest-cov`: 代码覆盖率

### 11.2 集成测试

**测试场景:**
- 完整的邮件提取流程
- 多账号处理
- 错误恢复

### 11.3 性能测试

**测试指标:**
- 1000封邮件处理时间
- 内存使用峰值
- 大附件处理性能

---

## 12. 依赖包列表

### 12.1 requirements.txt

```txt
# 核心依赖
python-dotenv>=1.0.0        # 环境变量管理
chardet>=5.0.0              # 字符编码检测

# 可选依赖
psycopg2-binary>=2.9.0      # PostgreSQL支持
pymysql>=1.0.0              # MySQL支持

# 开发依赖
pytest>=7.0.0               # 测试框架
pytest-cov>=4.0.0           # 代码覆盖率
black>=23.0.0               # 代码格式化
flake8>=6.0.0               # 代码检查
mypy>=1.0.0                 # 类型检查
```

---

## 13. 开发规范

### 13.1 代码风格

- 遵循PEP 8
- 使用Black格式化
- 使用Flake8检查
- 使用MyPy类型检查

### 13.2 命名规范

- 类名: `PascalCase`
- 函数/变量: `snake_case`
- 常量: `UPPER_SNAKE_CASE`
- 私有成员: `_leading_underscore`

### 13.3 文档规范

- 所有公共接口必须有docstring
- 使用Google风格docstring
- 复杂逻辑添加注释

**示例:**
```python
def fetch_email(self, email_id: str) -> bytes:
    """
    获取单封邮件的原始数据.
    
    Args:
        email_id: 邮件唯一标识符
        
    Returns:
        邮件的原始字节数据
        
    Raises:
        IMAPOperationError: 获取失败时抛出
        
    Example:
        >>> client = IMAPClient('imap.gmail.com', 993)
        >>> raw_email = client.fetch_email('12345')
    """
    pass
```

---

## 14. 部署和使用

### 14.1 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/your-repo/email-connector.git
cd email-connector

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 复制配置文件
cp config/config.ini.example config/config.ini
cp config/.env.example .env

# 5. 编辑配置文件
nano .env  # 填入邮箱账号和密码
nano config/config.ini  # 根据需要调整配置

# 6. 运行程序
python src/main.py --help
```

### 14.2 打包分发

```bash
# 使用setuptools打包
python setup.py sdist bdist_wheel

# 安装到系统
pip install dist/email_connector-1.0.0-py3-none-any.whl

# 使用命令
email-connector --help
```

---

## 15. 未来路线图

### 15.1 短期目标 (1-3个月)

- [x] 核心功能开发
- [ ] 单元测试覆盖
- [ ] 性能优化
- [ ] 文档完善

### 15.2 中期目标 (3-6个月)

- [ ] POP3协议支持
- [ ] 数据库输出支持
- [ ] Web界面
- [ ] 多语言支持

### 15.3 长期目标 (6-12个月)

- [ ] OAuth2认证
- [ ] 插件系统
- [ ] 云端部署
- [ ] 企业级功能(批量账号、权限管理)

---

## 16. 总结

本架构设计文档为IMAP邮件提取和CSV导出系统提供了完整的技术蓝图,具有以下特点:

✅ **模块化设计**: 清晰的模块划分,职责明确
✅ **高可扩展性**: 支持POP3、数据库、Web等多种扩展
✅ **安全可靠**: 完善的认证和错误处理机制
✅ **性能优化**: 流式处理、批量操作、并发支持
✅ **易于维护**: 规范的代码风格和文档
✅ **用户友好**: 灵活的CLI接口和配置选项

通过遵循本架构设计,可以构建一个专业、稳定、高效的邮件处理系统。

---

**文档版本**: 1.0.0  
**创建日期**: 2024-01-15  
**最后更新**: 2024-01-15  
**作者**: Email Connector Team