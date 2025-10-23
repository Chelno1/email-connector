# 日志系统使用指南

## 概述

本项目的日志系统提供了统一的日志记录接口,支持控制台和文件双输出,并与 [`ConfigManager`](../src/utils/config_manager.py:1) 无缝集成。

## 核心功能

- ✅ 控制台和文件双输出
- ✅ 从 [`ConfigManager`](../src/utils/config_manager.py:1) 读取配置
- ✅ 支持多日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ 日志文件自动轮转 (单文件最大10MB,保留5个备份)
- ✅ 为不同模块提供独立的logger实例
- ✅ 性能监控装饰器
- ✅ 线程安全
- ✅ 可选彩色日志支持 (需安装 `colorlog`)

## 快速开始

### 1. 基本使用

```python
from src.utils import setup_logging, get_logger
from src.utils.config_manager import ConfigManager

# 初始化配置和日志
config = ConfigManager()
setup_logging(config)

# 获取logger实例
logger = get_logger(__name__)

# 记录日志
logger.info("应用启动成功")
logger.error("发生错误")
```

### 2. 配置日志级别

在 `.env` 文件中配置:

```env
# 日志级别
LOG_LEVEL=INFO

# 日志格式
LOG_FORMAT=[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s

# 日志文件路径
LOG_FILE=logs/app.log
```

## 日志级别说明

| 级别 | 用途 | 示例 |
|------|------|------|
| **DEBUG** | 详细的调试信息 | `logger.debug("变量值: x=10")` |
| **INFO** | 一般信息消息 | `logger.info("邮件处理完成")` |
| **WARNING** | 警告信息 | `logger.warning("连接超时,正在重试")` |
| **ERROR** | 错误信息 | `logger.error("无法连接到服务器")` |
| **CRITICAL** | 严重错误 | `logger.critical("系统崩溃")` |

## 高级功能

### 1. 性能监控

使用 [`@log_performance`](../src/utils/logger.py:256) 装饰器监控函数执行时间:

```python
from src.utils import log_performance

@log_performance
def fetch_emails():
    # 邮件获取逻辑
    pass

# 日志输出: 执行完成: fetch_emails - 耗时: 2.345秒
```

### 2. 函数调用日志

使用 [`@log_function_call`](../src/utils/logger.py:298) 装饰器记录函数调用(需DEBUG级别):

```python
from src.utils import log_function_call

@log_function_call
def process_email(email_id: str, save_attachment: bool = True):
    pass

# 日志输出: 调用函数: process_email - args=('12345',), kwargs={'save_attachment': True}
```

### 3. 日志上下文管理

使用 [`LogContext`](../src/utils/logger.py:319) 临时改变日志级别:

```python
from src.utils import get_logger, LogContext
import logging

logger = get_logger(__name__)

# 临时使用DEBUG级别
with LogContext(logger, level=logging.DEBUG):
    logger.debug("这条DEBUG日志只在此代码块中可见")

# 恢复原日志级别
```

### 4. 便利函数

直接使用根logger记录日志:

```python
from src.utils.logger import info, warning, error

info("快速记录INFO日志")
warning("快速记录WARNING日志")
error("快速记录ERROR日志")
```

### 5. 异常日志记录

记录异常信息和堆栈跟踪:

```python
logger = get_logger(__name__)

try:
    result = 10 / 0
except ZeroDivisionError as e:
    # 记录异常和堆栈跟踪
    logger.error(f"发生除零错误: {e}", exc_info=True)
```

## 最佳实践

### 1. 模块级Logger

在每个模块中创建专用logger:

```python
# src/core/imap_client.py
from src.utils import get_logger

logger = get_logger(__name__)

class IMAPClient:
    def connect(self):
        logger.info("正在连接到IMAP服务器...")
```

### 2. 日志消息格式

使用清晰、描述性的日志消息:

```python
# ✅ 好的做法
logger.info(f"成功处理 {count} 封邮件")
logger.error(f"连接失败: {error_msg}")

# ❌ 不好的做法
logger.info("done")
logger.error("err")
```

### 3. 敏感信息处理

避免在日志中记录敏感信息:

```python
# ❌ 不要这样做
logger.info(f"密码: {password}")

# ✅ 应该这样做
logger.info("认证成功")
```

### 4. 性能关键代码

在性能关键的代码中使用条件日志:

```python
if logger.isEnabledFor(logging.DEBUG):
    # 只在DEBUG级别时执行耗时的字符串格式化
    logger.debug(f"详细信息: {expensive_operation()}")
```

## 日志格式说明

### 控制台输出

简化格式,便于快速查看:

```
[2025-10-23 15:05:44] [INFO] 应用启动成功
[2025-10-23 15:05:45] [ERROR] 连接失败
```

### 文件输出

详细格式,包含文件名和行号:

```
[2025-10-23 15:05:44] [INFO] [logger.py:103] 日志系统初始化成功
[2025-10-23 15:05:44] [INFO] [main.py:45] 应用启动成功
[2025-10-23 15:05:45] [ERROR] [imap_client.py:78] 连接失败: Connection timeout
```

## 日志文件管理

### 自动轮转

日志系统使用 [`RotatingFileHandler`](../src/utils/logger.py:190),自动管理日志文件:

- **最大文件大小**: 10MB
- **备份文件数量**: 5个
- **文件命名**: `app.log`, `app.log.1`, `app.log.2`, ..., `app.log.5`

### 手动清理

```bash
# 删除所有日志文件
rm -rf logs/*.log*

# 删除旧的备份文件
find logs/ -name "*.log.*" -mtime +30 -delete
```

## 彩色日志支持

安装 `colorlog` 以启用彩色控制台输出:

```bash
pip install colorlog
```

日志颜色映射:
- **DEBUG**: 青色
- **INFO**: 绿色
- **WARNING**: 黄色
- **ERROR**: 红色
- **CRITICAL**: 粗体红色

## 故障排除

### 问题1: 日志文件未创建

**原因**: 日志目录不存在或无写入权限

**解决方案**:
```bash
# 创建日志目录
mkdir -p logs

# 设置权限
chmod 755 logs
```

### 问题2: 日志级别不生效

**原因**: 配置优先级问题

**解决方案**: 检查配置优先级
1. 命令行参数 (`--log-level`)
2. 环境变量 (`.env` 中的 `LOG_LEVEL`)
3. 默认值 (`INFO`)

### 问题3: 重复日志输出

**原因**: 多次初始化日志系统

**解决方案**:
```python
# 使用 reset_logging 重置
from src.utils import reset_logging
reset_logging()
setup_logging(config)
```

## 示例代码

完整示例请参考 [`examples/logger_usage.py`](../examples/logger_usage.py:1)

运行示例:
```bash
python examples/logger_usage.py
```

## 相关文档

- [配置管理器指南](config_manager_guide.md:1)
- [架构设计文档 - 日志系统](../architecture.md:541)

## API参考

### 核心函数

- [`setup_logging(config_manager)`](../src/utils/logger.py:46) - 初始化日志系统
- [`get_logger(name)`](../src/utils/logger.py:219) - 获取logger实例
- [`log_performance(func)`](../src/utils/logger.py:256) - 性能监控装饰器
- [`log_function_call(func)`](../src/utils/logger.py:298) - 函数调用日志装饰器
- [`reset_logging()`](../src/utils/logger.py:380) - 重置日志系统

### 便利函数

- [`debug(msg)`](../src/utils/logger.py:396) - 记录DEBUG日志
- [`info(msg)`](../src/utils/logger.py:401) - 记录INFO日志
- [`warning(msg)`](../src/utils/logger.py:406) - 记录WARNING日志
- [`error(msg)`](../src/utils/logger.py:411) - 记录ERROR日志
- [`critical(msg)`](../src/utils/logger.py:416) - 记录CRITICAL日志

---

**最后更新**: 2025-10-23  
**版本**: 1.0.0