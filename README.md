# Email Connector

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

专业级IMAP邮件提取和CSV导出工具 - 安全、高效、易用的邮件数据处理解决方案

## 📋 目录

- [功能特性](#功能特性)
- [系统要求](#系统要求)
- [安装指南](#安装指南)
- [快速开始](#快速开始)
- [详细使用](#详细使用)
- [配置说明](#配置说明)
- [CSV输出格式](#csv输出格式)
- [常见邮箱配置](#常见邮箱配置)
- [常见问题](#常见问题)
- [项目架构](#项目架构)
- [开发指南](#开发指南)
- [许可证](#许可证)
- [贡献](#贡献)

## ✨ 功能特性

- ✅ **IMAP协议支持** - 标准IMAP协议,兼容主流邮箱服务
- ✅ **安全认证** - 支持SSL/TLS加密连接,保护账户安全
- ✅ **灵活筛选** - 多维度邮件筛选(日期、状态、关键词、发件人等)
- ✅ **完整解析** - 支持MIME多部分邮件、HTML/纯文本内容
- ✅ **附件处理** - 自动识别和保存邮件附件
- ✅ **批量处理** - 高效的批量邮件获取和处理
- ✅ **结构化导出** - 标准CSV格式,易于数据分析
- ✅ **命令行接口** - 简洁直观的CLI命令
- ✅ **配置管理** - 灵活的配置系统(环境变量/.env文件)
- ✅ **日志系统** - 详细的操作日志和错误追踪
- ✅ **错误处理** - 完善的异常处理和友好的错误提示

## 📦 系统要求

- **Python版本**: Python 3.8 或更高版本
- **操作系统**: Linux / macOS / Windows
- **网络要求**: 能够访问邮箱IMAP服务器
- **存储空间**: 根据邮件数量和附件大小而定

## 🚀 安装指南

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/email-connector.git
cd email-connector
```

### 2. 安装 uv (Python 包管理工具)

uv 是一个极快的 Python 包和项目管理器。

**Linux/macOS**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows**:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

或者使用 pip 安装:
```bash
pip install uv
```

### 3. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 使用 uv 安装依赖
uv pip sync requirements.txt
# 或者
uv pip install -r requirements.txt
```

**提示**: 使用 `uv pip sync` 可以确保环境与 requirements.txt 完全一致,会移除未列出的包。

### 4. 配置邮箱

复制示例配置文件:

```bash
cp config/.env.example .env
```

编辑 `.env` 文件,填入你的邮箱信息:

```env
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
EMAIL_USER=your.email@gmail.com
EMAIL_PASSWORD=your_app_password
```

**⚠️ 安全提示**: 
- 切勿将 `.env` 文件提交到版本控制系统
- 建议使用应用专用密码而非主密码
- 定期更换密码,保障账户安全

## 🎯 快速开始

### 基本用法

```bash
# 获取所有邮件并导出到CSV
python email_connector.py

# 获取最近10封未读邮件
python email_connector.py --unseen --limit 10

# 指定输出文件
python email_connector.py --output my_emails.csv
```

### 按日期筛选

```bash
# 获取指定日期范围的邮件
python email_connector.py --from-date 2024-01-01 --to-date 2024-01-31

# 获取最近7天的邮件
python email_connector.py --from-date 2024-01-15
```

### 高级筛选

```bash
# 按发件人筛选
python email_connector.py --sender "boss@company.com"

# 按主题关键词筛选
python email_connector.py --subject "重要通知"

# 组合筛选:未读邮件+特定发件人+日期范围
python email_connector.py --unseen --sender "client@example.com" --from-date 2024-01-01
```

## 📖 详细使用

### CLI参数完整列表

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `--host` | 文本 | IMAP服务器地址 | `--host imap.gmail.com` |
| `--port` | 数字 | IMAP服务器端口 | `--port 993` |
| `--email` | 文本 | 邮箱账号 | `--email user@gmail.com` |
| `--password` | 文本 | 邮箱密码 | `--password "your_password"` |
| `--folder` | 文本 | 邮箱文件夹 | `--folder INBOX` |
| `--output` | 文本 | CSV输出完整路径 | `--output /path/to/emails.csv` |
| `--filename` | 文本 | CSV文件名(仅文件名) | `--filename my-emails` |
| `--limit` | 数字 | 限制邮件数量 | `--limit 100` |
| `--from-date` | 日期 | 起始日期(YYYY-MM-DD) | `--from-date 2024-01-01` |
| `--to-date` | 日期 | 结束日期(YYYY-MM-DD) | `--to-date 2024-12-31` |
| `--unseen` | 开关 | 仅获取未读邮件 | `--unseen` |
| `--sender` | 文本 | 按发件人筛选 | `--sender "boss@company.com"` |
| `--subject` | 文本 | 按主题关键词筛选 | `--subject "报告"` |
| `--attachment-dir` | 文本 | 附件保存目录 | `--attachment-dir ./files` |
| `--no-attachments` | 开关 | 禁用附件保存 | `--no-attachments` |
| `--mark-as-read` | 开关 | 处理后标记为已读 | `--mark-as-read` |
| `--log-level` | 文本 | 日志级别 | `--log-level DEBUG` |

### 使用场景示例

#### 1. 导出所有邮件

```bash
python email_connector.py --output all_emails.csv
```

#### 2. 获取未读邮件并保存附件(默认保存到output/attachments)

```bash
python email_connector.py \
  --unseen \
  --filename unread_emails
  
# 或指定附件目录
python email_connector.py \
  --unseen \
  --attachment-dir ./my-attachments \
  --filename unread_emails
  
# 如果不想保存附件
python email_connector.py \
  --unseen \
  --no-attachments \
  --filename unread_emails
```

#### 3. 按月份导出邮件

```bash
python email_connector.py \
  --from-date 2024-01-01 \
  --to-date 2024-01-31 \
  --output january_2024.csv
```

#### 4. 筛选特定发件人的重要邮件

```bash
python email_connector.py \
  --sender "client@important.com" \
  --subject "合同" \
  --from-date 2024-01-01 \
  --save-attachments \
  --output important_contracts.csv
```

#### 5. 批量处理未读邮件并标记已读

```bash
python email_connector.py \
  --unseen \
  --limit 50 \
  --mark-read \
  --output processed_emails.csv
```

#### 6. 使用自定义IMAP服务器

```bash
python email_connector.py \
  --host mail.company.com \
  --port 993 \
  --user john@company.com \
  --password "secure_password" \
  --folder Inbox/Work \
  --output work_emails.csv
```

## ⚙️ 配置说明

### .env 配置文件

项目支持通过 `.env` 文件配置默认参数:

```env
# IMAP服务器配置
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USE_SSL=true

# 邮箱认证
EMAIL_ACCOUNT=your.email@gmail.com
EMAIL_PASSWORD=your_app_password

# 默认邮箱文件夹
DEFAULT_FOLDER=INBOX

# 输出配置
OUTPUT_CSV_DIR=output/csv
OUTPUT_CSV_FILENAME=
OUTPUT_ATTACHMENT_DIR=output/attachments
OUTPUT_SAVE_ATTACHMENTS=true

# 邮件处理配置
DEFAULT_LIMIT=100
MAX_TEXT_LENGTH=10000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5
```

### 配置优先级

配置加载优先级(从高到低):
1. 命令行参数
2. 环境变量
3. `.env` 文件
4. 默认值

示例:

```bash
# 命令行参数会覆盖.env中的配置
python email_connector.py --host imap.outlook.com --port 993
```

## 📄 CSV输出格式

导出的CSV文件包含以下字段:

| 字段名 | 说明 | 示例 |
|--------|------|------|
| `email_account` | 邮箱账户 | `user@gmail.com` |
| `message_id` | 邮件唯一标识 | `<abc123@gmail.com>` |
| `thread_id` | 会话ID | `<thread123>` |
| `subject` | 邮件主题 | `重要通知` |
| `date` | 发送日期时间 | `2024-01-15 14:30:00` |
| `from` | 发件人 | `张三 <sender@example.com>` |
| `to` | 收件人列表 | `用户1 <user1@example.com>; user2@example.com` |
| `cc` | 抄送列表 | `cc@example.com` |
| `body_text` | 纯文本内容 | `邮件正文...` |
| `has_attachment` | 是否有附件 | `True/False` |
| `attachment_names` | 附件文件名列表 | `file1.pdf;file2.doc` |
| `attachment_paths` | 附件本地保存路径 | `/path/to/file1.pdf;/path/to/file2.doc` |
| `attachment_count` | 附件数量 | `2` |
| `labels` | 邮件标签 | `Important;Work` |

**CSV示例**:

```csv
email_account,message_id,subject,date,from,has_attachment,attachment_names,attachment_paths
user@gmail.com,<abc@example.com>,周会通知,2024-01-15 10:00:00,老板 <boss@company.com>,False,,0
user@gmail.com,<def@example.com>,合同文件,2024-01-15 11:30:00,客户 <client@partner.com>,True,contract.pdf,/home/user/output/attachments/20240115/contract.pdf,1
```

**注意**: `attachment_paths` 字段只有在附件被保存后才会有值，如果使用 `--no-attachments` 参数，该字段将为空。

## 🔧 常见邮箱配置

### Gmail

```env
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
EMAIL_USER=your.email@gmail.com
EMAIL_PASSWORD=your_app_password
```

**注意**: Gmail需要使用[应用专用密码](https://support.google.com/accounts/answer/185833)

### Outlook / Hotmail

```env
IMAP_HOST=imap-mail.outlook.com
IMAP_PORT=993
EMAIL_USER=your.email@outlook.com
EMAIL_PASSWORD=your_password
```

### QQ邮箱

```env
IMAP_HOST=imap.qq.com
IMAP_PORT=993
EMAIL_USER=your_qq_number@qq.com
EMAIL_PASSWORD=authorization_code
```

**注意**: QQ邮箱需要使用授权码,在邮箱设置中生成

### 163邮箱

```env
IMAP_HOST=imap.163.com
IMAP_PORT=993
EMAIL_USER=your.email@163.com
EMAIL_PASSWORD=authorization_code
```

### 企业邮箱(Exchange)

```env
IMAP_HOST=outlook.office365.com
IMAP_PORT=993
EMAIL_USER=your.email@company.com
EMAIL_PASSWORD=your_password
```

## ❓ 常见问题

### Q1: 连接邮箱失败怎么办?

**A**: 检查以下几点:
1. 确认IMAP服务器地址和端口正确
2. 检查用户名和密码是否正确
3. 确认邮箱已开启IMAP服务
4. 对于Gmail等服务,确保使用应用专用密码
5. 检查防火墙是否阻止连接

### Q2: 如何处理大量邮件?

**A**: 建议策略:
```bash
# 分批处理,每次处理100封
python email_connector.py --limit 100 --output batch1.csv

# 或按日期范围分段处理
python email_connector.py --from-date 2024-01-01 --to-date 2024-01-31 --output jan.csv
python email_connector.py --from-date 2024-02-01 --to-date 2024-02-29 --output feb.csv
```

### Q3: 附件保存在哪里?

**A**:
- **默认行为**: 程序会自动保存附件到 `output/attachments/` 目录
- **自定义位置**: 使用 `--attachment-dir` 参数指定其他目录
- **禁用保存**: 使用 `--no-attachments` 参数禁用附件保存
- 附件按邮件日期分目录存储(如: `output/attachments/20240115/`)

### Q4: CSV文件中文乱码怎么办?

**A**: 
- CSV文件使用UTF-8编码
- Excel打开时选择UTF-8编码
- 或使用专业CSV工具(如VS Code)打开

### Q5: 如何只获取未读邮件?

**A**:
```bash
python email_connector.py --unseen
```

### Q6: 支持哪些日期格式?

**A**: 
- 标准格式: `YYYY-MM-DD`
- 示例: `2024-01-15`

### Q7: 如何启用调试日志?

**A**:
```bash
python email_connector.py --log-level DEBUG
```

### Q8: 程序运行很慢怎么办?

**A**: 
- 使用 `--limit` 限制邮件数量
- 使用日期范围缩小查询范围
- 检查网络连接速度
- 避免在高峰时段运行

## 🏗️ 项目架构

```
email-connector/
├── src/
│   ├── models/              # 数据模型
│   │   ├── email_message.py # 邮件消息模型
│   │   └── attachment.py    # 附件模型
│   ├── core/                # 核心功能
│   │   ├── imap_client.py   # IMAP客户端
│   │   ├── email_parser.py  # 邮件解析器
│   │   └── csv_writer.py    # CSV写入器
│   ├── utils/               # 工具模块
│   │   ├── config_manager.py # 配置管理
│   │   └── logger.py        # 日志系统
│   ├── cli.py               # 命令行接口
│   └── main.py              # 主程序
├── config/                  # 配置文件
│   └── .env.example         # 配置示例
├── examples/                # 使用示例
├── docs/                    # 文档
├── tests/                   # 测试(待完善)
├── email_connector.py       # 程序入口点
├── requirements.txt         # 依赖清单
├── setup.py                 # 包配置
└── README.md               # 本文件
```

### 核心模块说明

- **IMAPClient**: IMAP协议客户端,负责邮箱连接和邮件获取
- **EmailParser**: 邮件解析器,处理MIME格式和内容提取
- **CSVWriter**: CSV写入器,负责数据序列化和文件写入
- **ConfigManager**: 配置管理器,处理环境变量和配置文件
- **Logger**: 日志系统,提供结构化日志记录

## 🛠️ 开发指南

### 开发环境设置

```bash
# 创建虚拟环境(如果还没有)
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows

# 安装项目依赖
uv pip sync requirements.txt

# 安装开发依赖(如果有 setup.py)
uv pip install -e .[dev]

# 运行测试(待完善)
pytest tests/

# 代码格式化
black src/

# 类型检查
mypy src/
```

**提示**: 如果需要添加新的依赖包,使用:
```bash
# 添加新包
uv pip install package_name

# 更新 requirements.txt
uv pip freeze > requirements.txt
```

### 代码规范

- 遵循PEP 8代码风格
- 使用Black进行代码格式化
- 添加类型注解(Type Hints)
- 编写文档字符串(Docstrings)

### 贡献流程

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 📜 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🤝 贡献

欢迎贡献代码!如果你有好的想法或发现了问题:

1. 提交Issue描述问题或建议
2. Fork项目并创建Pull Request
3. 更新文档和测试

### 贡献者

感谢所有贡献者的付出!

## 📞 联系方式

- 项目主页: [https://github.com/yourusername/email-connector](https://github.com/yourusername/email-connector)
- 问题反馈: [https://github.com/yourusername/email-connector/issues](https://github.com/yourusername/email-connector/issues)

## 🙏 致谢

- 感谢Python社区的支持
- 感谢所有开源项目的贡献者

---

**⭐ 如果这个项目对你有帮助,请给个Star支持一下!**