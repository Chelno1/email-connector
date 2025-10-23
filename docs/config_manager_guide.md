# 配置管理器使用指南

## 概述

`ConfigManager` 是email-connector项目的配置管理核心模块,负责从 `.env` 文件和命令行参数加载所有配置。

## 特性

- ✅ 单例模式,确保配置只加载一次
- ✅ 支持从 `.env` 文件加载配置
- ✅ 支持命令行参数覆盖
- ✅ 配置优先级: 命令行 > 环境变量 > 默认值
- ✅ 完整的配置验证功能
- ✅ 类型安全的配置访问接口

## 快速开始

### 1. 安装依赖

```bash
pip install python-dotenv
```

### 2. 创建配置文件

```bash
# 复制示例配置文件
cp config/.env.example .env

# 编辑配置文件,填入实际的配置值
nano .env
```

### 3. 使用配置管理器

```python
from src.utils import ConfigManager, ConfigError

# 初始化配置管理器
config = ConfigManager()

# 获取IMAP配置
imap_config = config.get_imap_config()
print(f"IMAP服务器: {imap_config['host']}")

# 获取邮箱认证信息
try:
    email, password = config.get_email_credentials()
    print(f"邮箱: {email}")
except ConfigError as e:
    print(f"配置错误: {e}")

# 验证配置
try:
    config.validate()
    print("配置验证通过")
except ConfigError as e:
    print(f"配置验证失败: {e}")
```

## 配置项说明

### 必需配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `EMAIL_ACCOUNT` | 邮箱账号 | `user@gmail.com` |
| `EMAIL_PASSWORD` | 邮箱密码或应用专用密码 | `your-app-password` |

### IMAP配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `IMAP_HOST` | `imap.gmail.com` | IMAP服务器地址 |
| `IMAP_PORT` | `993` | IMAP端口 |
| `IMAP_USE_SSL` | `true` | 是否使用SSL |
| `IMAP_TIMEOUT` | `30` | 连接超时(秒) |

### 邮件配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `EMAIL_FOLDER` | `INBOX` | 邮箱文件夹 |
| `EMAIL_MARK_AS_READ` | `false` | 是否标记为已读 |
| `EMAIL_BATCH_SIZE` | `50` | 批处理大小 |

### 筛选配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `FILTER_ENABLED` | `true` | 是否启用筛选 |
| `FILTER_DEFAULT_LIMIT` | `1000` | 默认邮件数量限制 |

### 输出配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `OUTPUT_CSV_DIR` | `output/csv` | CSV输出目录 |
| `OUTPUT_CSV_FILENAME` | `` | CSV文件名(空则自动生成) |
| `OUTPUT_ATTACHMENT_DIR` | `output/attachments` | 附件目录 |
| `OUTPUT_SAVE_ATTACHMENTS` | `true` | 是否保存附件 |

### 日志配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `LOG_FORMAT` | `[%(asctime)s] [%(levelname)s] ...` | 日志格式 |
| `LOG_FILE` | `logs/app.log` | 日志文件路径 |

## API参考

### ConfigManager类

#### `__init__(env_path=None, cli_args=None)`

初始化配置管理器。

**参数:**
- `env_path` (str, 可选): `.env` 文件路径,默认为项目根目录下的 `.env`
- `cli_args` (dict, 可选): 命令行参数字典

#### `get_imap_config() -> dict`

获取IMAP配置。

**返回:**
```python
{
    'host': str,
    'port': int,
    'use_ssl': bool,
    'timeout': int
}
```

#### `get_email_credentials() -> tuple`

获取邮箱认证信息。

**返回:** `(email: str, password: str)`

**异常:** `ConfigError` - 认证信息缺失时抛出

#### `get_email_config() -> dict`

获取邮件相关配置。

#### `get_filter_config() -> dict`

获取筛选配置。

#### `get_output_config() -> dict`

获取输出配置。

#### `get_logging_config() -> dict`

获取日志配置。

#### `validate() -> bool`

验证配置完整性。

**异常:** `ConfigError` - 配置验证失败时抛出

#### `get(key, default=None, value_type=str) -> Any`

获取单个配置值。

**参数:**
- `key` (str): 配置键(环境变量格式,如 `'IMAP_HOST'`)
- `default` (Any): 默认值
- `value_type` (type): 值类型(用于类型转换)

## 配置优先级

配置值的获取遵循以下优先级:

```
命令行参数 > 环境变量 > 默认值
```

### 示例

假设:
- `.env` 文件中: `IMAP_HOST=imap.gmail.com`
- 命令行参数: `--host=imap.custom.com`

最终使用的值为: `imap.custom.com` (命令行参数优先)

## 使用示例

完整的使用示例请参考: [`examples/config_usage.py`](../examples/config_usage.py)

运行示例:

```bash
python examples/config_usage.py
```

## 错误处理

配置管理器定义了 `ConfigError` 异常类,用于处理配置相关的错误:

```python
from src.utils import ConfigManager, ConfigError

try:
    config = ConfigManager()
    config.validate()
except ConfigError as e:
    print(f"配置错误: {e}")
    # 处理错误...
```

## 常见问题

### Q: 为什么会报 "邮箱账号未配置" 错误?

A: 请确保在 `.env` 文件中设置了 `EMAIL_ACCOUNT` 和 `EMAIL_PASSWORD`。

### Q: 如何使用Gmail的应用专用密码?

A: 
1. 登录Google账号
2. 进入 "安全性" 设置
3. 启用 "两步验证"
4. 生成 "应用专用密码"
5. 将生成的密码填入 `.env` 文件的 `EMAIL_PASSWORD`

### Q: 配置文件路径是相对路径还是绝对路径?

A: 支持两种方式:
- 相对路径会相对于项目根目录解析
- 绝对路径直接使用

### Q: 如何在代码中覆盖配置?

A: 使用 `cli_args` 参数:

```python
config = ConfigManager(cli_args={
    'host': 'custom.imap.com',
    'port': 995
})
```

## 贡献

如需添加新的配置项,请:

1. 在 `.env.example` 中添加配置说明
2. 在 `ConfigManager._defaults` 中添加默认值
3. 在 `ConfigManager._load_env()` 中添加环境变量键名
4. 更新本文档

---

**最后更新**: 2024-01-15
**版本**: 1.0.0