"""
IMAP客户端使用示例

展示如何使用IMAPClient进行邮件操作,包括:
- 基本连接和登录
- 列出文件夹
- 搜索邮件
- 批量获取邮件
- 标记邮件状态
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.imap_client import IMAPClient, IMAPError
from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logging, get_logger


def example_basic_usage():
    """示例1: 基本连接和登录"""
    print("\n" + "="*60)
    print("示例1: 基本连接和登录")
    print("="*60)
    
    # 初始化配置和日志
    config = ConfigManager()
    setup_logging(config)
    logger = get_logger(__name__)
    
    # 创建IMAP客户端
    client = IMAPClient(config, logger)
    
    try:
        # 连接到服务器
        client.connect()
        print("✓ 成功连接到IMAP服务器")
        
        # 获取认证信息并登录
        email, password = config.get_email_credentials()
        client.login(email, password)
        print(f"✓ 成功登录邮箱: {email}")
        
    except IMAPError as e:
        print(f"✗ 错误: {e}")
    finally:
        # 断开连接
        client.disconnect()
        print("✓ 已断开连接")


def example_list_folders():
    """示例2: 列出所有文件夹"""
    print("\n" + "="*60)
    print("示例2: 列出所有文件夹")
    print("="*60)
    
    config = ConfigManager()
    
    with IMAPClient(config) as client:
        try:
            client.connect()
            email, password = config.get_email_credentials()
            client.login(email, password)
            
            # 列出所有文件夹
            folders = client.list_folders()
            print(f"\n找到 {len(folders)} 个文件夹:")
            for i, folder in enumerate(folders, 1):
                print(f"  {i}. {folder}")
            
            # 获取INBOX状态
            status = client.get_folder_status("INBOX")
            print(f"\nINBOX 状态:")
            print(f"  总邮件数: {status.get('messages', 0)}")
            print(f"  未读邮件: {status.get('unseen', 0)}")
            print(f"  最近邮件: {status.get('recent', 0)}")
            
        except IMAPError as e:
            print(f"✗ 错误: {e}")


def example_search_messages():
    """示例3: 搜索邮件"""
    print("\n" + "="*60)
    print("示例3: 搜索邮件")
    print("="*60)
    
    config = ConfigManager()
    
    with IMAPClient(config) as client:
        try:
            client.connect()
            email, password = config.get_email_credentials()
            client.login(email, password)
            
            # 搜索所有邮件
            all_uids = client.search_messages(folder="INBOX", criteria="ALL")
            print(f"✓ INBOX中共有 {len(all_uids)} 封邮件")
            
            # 搜索未读邮件
            unseen_uids = client.get_unseen_messages()
            print(f"✓ 未读邮件: {len(unseen_uids)} 封")
            
            # 获取最新10封邮件
            latest_uids = client.get_latest_messages(limit=10)
            print(f"✓ 最新10封邮件的UID: {latest_uids}")
            
            # 按日期范围搜索(需要根据实际情况调整日期)
            # date_uids = client.get_messages_by_date(
            #     since_date="01-Jan-2024",
            #     before_date="31-Jan-2024"
            # )
            # print(f"✓ 2024年1月的邮件: {len(date_uids)} 封")
            
        except IMAPError as e:
            print(f"✗ 错误: {e}")


def example_fetch_messages():
    """示例4: 批量获取邮件"""
    print("\n" + "="*60)
    print("示例4: 批量获取邮件")
    print("="*60)
    
    config = ConfigManager()
    
    with IMAPClient(config) as client:
        try:
            client.connect()
            email, password = config.get_email_credentials()
            client.login(email, password)
            
            # 获取最新5封邮件
            uids = client.get_latest_messages(limit=5)
            print(f"准备获取 {len(uids)} 封邮件\n")
            
            # 批量获取邮件
            for i, (uid, raw_email) in enumerate(client.fetch_messages_batch(uids, batch_size=2), 1):
                print(f"  {i}. UID: {uid}, 大小: {len(raw_email)} bytes")
            
            print(f"\n✓ 成功获取 {len(uids)} 封邮件")
            
        except IMAPError as e:
            print(f"✗ 错误: {e}")


def example_message_status():
    """示例5: 邮件状态管理"""
    print("\n" + "="*60)
    print("示例5: 邮件状态管理")
    print("="*60)
    
    config = ConfigManager()
    
    with IMAPClient(config) as client:
        try:
            client.connect()
            email, password = config.get_email_credentials()
            client.login(email, password)
            
            # 获取未读邮件
            unseen_uids = client.get_unseen_messages()
            
            if unseen_uids:
                print(f"找到 {len(unseen_uids)} 封未读邮件")
                
                # 标记前3封为已读(如果有的话)
                if len(unseen_uids) >= 3:
                    uids_to_mark = unseen_uids[:3]
                    client.mark_as_read(uids_to_mark)
                    print(f"✓ 已标记 {len(uids_to_mark)} 封邮件为已读")
                    
                    # 再次检查未读邮件数
                    new_unseen = client.get_unseen_messages()
                    print(f"✓ 现在未读邮件: {len(new_unseen)} 封")
            else:
                print("没有未读邮件")
            
        except IMAPError as e:
            print(f"✗ 错误: {e}")


def example_context_manager():
    """示例6: 使用上下文管理器"""
    print("\n" + "="*60)
    print("示例6: 使用上下文管理器")
    print("="*60)
    
    config = ConfigManager()
    
    # 使用with语句,自动管理连接
    with IMAPClient(config) as client:
        client.connect()
        email, password = config.get_email_credentials()
        client.login(email, password)
        
        # 执行操作
        uids = client.search_messages(limit=10)
        print(f"✓ 找到 {len(uids)} 封邮件")
        
        # 退出with块时自动断开连接
    
    print("✓ 连接已自动清理")


def example_error_handling():
    """示例7: 错误处理"""
    print("\n" + "="*60)
    print("示例7: 错误处理")
    print("="*60)
    
    from src.core.imap_client import (
        IMAPConnectionError,
        IMAPAuthenticationError,
        IMAPOperationError
    )
    
    config = ConfigManager()
    client = IMAPClient(config)
    
    # 1. 连接错误示例
    print("\n1. 测试连接到无效服务器:")
    try:
        # 临时修改配置(仅用于演示)
        original_host = config.env_vars.get('IMAP_HOST')
        config.env_vars['IMAP_HOST'] = 'invalid.server.com'
        
        client.connect()
    except IMAPConnectionError as e:
        print(f"  ✓ 捕获到连接错误: {e}")
    finally:
        # 恢复原配置
        if original_host:
            config.env_vars['IMAP_HOST'] = original_host
    
    # 2. 认证错误示例
    print("\n2. 测试无效认证:")
    try:
        client.connect()
        client.login("invalid@example.com", "wrong_password")
    except IMAPAuthenticationError as e:
        print(f"  ✓ 捕获到认证错误: {e}")
    except IMAPConnectionError:
        print("  (跳过此测试 - 连接失败)")
    finally:
        client.disconnect()
    
    # 3. 操作错误示例
    print("\n3. 测试未连接时执行操作:")
    try:
        new_client = IMAPClient(config)
        # 尝试在未连接时搜索邮件
        new_client.search_messages()
    except IMAPConnectionError as e:
        print(f"  ✓ 捕获到操作错误: {e}")


def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("IMAP客户端使用示例")
    print("="*60)
    
    try:
        # 注意: 根据需要选择要运行的示例
        # 建议逐个运行以观察结果
        
        example_basic_usage()
        example_list_folders()
        example_search_messages()
        example_fetch_messages()
        # example_message_status()  # 谨慎使用,会修改邮件状态
        example_context_manager()
        example_error_handling()
        
        print("\n" + "="*60)
        print("所有示例执行完成!")
        print("="*60)
        
    except Exception as e:
        print(f"\n执行示例时发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 提示用户配置环境变量
    print("\n请确保已正确配置 .env 文件:")
    print("  - EMAIL_ACCOUNT: 邮箱账号")
    print("  - EMAIL_PASSWORD: 邮箱密码")
    print("  - IMAP_HOST: IMAP服务器地址")
    print("  - IMAP_PORT: IMAP端口(默认993)")
    print()
    
    input("按Enter键继续...")
    
    main()