"""
ConfigManager 使用示例

展示如何使用配置管理器加载和访问配置。
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import ConfigManager, ConfigError


def main():
    """主函数"""
    print("=" * 60)
    print("ConfigManager 使用示例")
    print("=" * 60)
    
    # 示例1: 基本用法
    print("\n【示例1】基本用法 - 从 .env 文件加载配置")
    print("-" * 60)
    
    try:
        # 初始化配置管理器
        config = ConfigManager()
        
        # 获取IMAP配置
        imap_config = config.get_imap_config()
        print(f"IMAP服务器: {imap_config['host']}")
        print(f"IMAP端口: {imap_config['port']}")
        print(f"使用SSL: {imap_config['use_ssl']}")
        print(f"超时时间: {imap_config['timeout']}秒")
        
    except ConfigError as e:
        print(f"配置错误: {e}")
    
    # 示例2: 获取邮箱认证信息
    print("\n【示例2】获取邮箱认证信息")
    print("-" * 60)
    
    try:
        email, password = config.get_email_credentials()
        print(f"邮箱账号: {email}")
        print(f"密码长度: {len(password)} 字符")
    except ConfigError as e:
        print(f"认证信息缺失: {e}")
        print("提示: 请在 .env 文件中配置 EMAIL_ACCOUNT 和 EMAIL_PASSWORD")
    
    # 示例3: 获取所有配置
    print("\n【示例3】获取所有配置")
    print("-" * 60)
    
    all_config = config.get_all_config()
    
    print("\n邮件配置:")
    for key, value in all_config['email'].items():
        print(f"  {key}: {value}")
    
    print("\n筛选配置:")
    for key, value in all_config['filter'].items():
        print(f"  {key}: {value}")
    
    print("\n输出配置:")
    for key, value in all_config['output'].items():
        print(f"  {key}: {value}")
    
    print("\n日志配置:")
    for key, value in all_config['logging'].items():
        print(f"  {key}: {value}")
    
    # 示例4: 使用命令行参数覆盖配置
    print("\n【示例4】使用命令行参数覆盖配置")
    print("-" * 60)
    
    cli_args = {
        'email': 'override@example.com',
        'host': 'imap.override.com',
        'port': 995,
        'limit': 500
    }
    
    config_with_cli = ConfigManager(cli_args=cli_args)
    
    print(f"IMAP服务器 (覆盖后): {config_with_cli.get_imap_config()['host']}")
    print(f"IMAP端口 (覆盖后): {config_with_cli.get_imap_config()['port']}")
    print(f"邮件限制 (覆盖后): {config_with_cli.get_filter_config()['limit']}")
    
    # 示例5: 配置验证
    print("\n【示例5】配置验证")
    print("-" * 60)
    
    try:
        config.validate()
        print("✓ 配置验证通过")
    except ConfigError as e:
        print(f"✗ 配置验证失败:\n{e}")
    
    # 示例6: 获取单个配置值
    print("\n【示例6】获取单个配置值")
    print("-" * 60)
    
    log_level = config.get('LOG_LEVEL', default='INFO', value_type=str)
    batch_size = config.get('EMAIL_BATCH_SIZE', default=50, value_type=int)
    save_attachments = config.get('OUTPUT_SAVE_ATTACHMENTS', default=True, value_type=bool)
    
    print(f"日志级别: {log_level}")
    print(f"批处理大小: {batch_size}")
    print(f"保存附件: {save_attachments}")
    
    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)


if __name__ == '__main__':
    main()