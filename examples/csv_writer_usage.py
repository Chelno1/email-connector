"""
CSV写入器使用示例

展示CSVWriter的各种用法:
- 基本CSV写入
- 批量写入邮件
- 使用上下文管理器
- 追加模式
- 自定义输出路径
- 错误处理
- 与IMAPClient和EmailParser集成
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.csv_writer import CSVWriter, CSVWriteError, create_csv_writer
from src.models.email_message import EmailMessage
from src.models.attachment import Attachment
from src.utils.config_manager import ConfigManager


def example_1_basic_usage():
    """示例1: 基本用法"""
    print("=" * 60)
    print("示例1: 基本CSV写入")
    print("=" * 60)
    
    # 创建测试邮件
    email = EmailMessage(
        email_account="user@gmail.com",
        message_id="<test123@mail.gmail.com>",
        subject="测试邮件",
        date=datetime.now(),
        from_address="sender@example.com",
        from_name="发件人",
        to_addresses=["recipient@example.com"],
        to_names=["收件人"],
        body_text="这是一封测试邮件的正文内容。"
    )
    
    # 创建CSV写入器
    writer = CSVWriter(output_path="output/example1.csv")
    
    try:
        writer.open()
        writer.write_message(email)
        print(f"✓ 邮件已写入: {writer.output_path}")
        print(f"✓ 写入统计: {writer.get_stats()}")
    finally:
        writer.close()


def example_2_context_manager():
    """示例2: 使用上下文管理器"""
    print("\n" + "=" * 60)
    print("示例2: 使用上下文管理器")
    print("=" * 60)
    
    # 创建多封测试邮件
    emails = []
    for i in range(3):
        email = EmailMessage(
            email_account="user@gmail.com",
            message_id=f"<test{i}@mail.gmail.com>",
            subject=f"测试邮件 #{i+1}",
            date=datetime.now(),
            from_address=f"sender{i}@example.com",
            from_name=f"发件人{i}",
            body_text=f"这是第 {i+1} 封测试邮件。"
        )
        emails.append(email)
    
    # 使用上下文管理器自动管理文件打开/关闭
    with CSVWriter(output_path="output/example2.csv") as writer:
        for email in emails:
            writer.write_message(email)
        print(f"✓ 已写入 {len(emails)} 封邮件")
        print(f"✓ 输出文件: {writer.output_path}")


def example_3_batch_write():
    """示例3: 批量写入"""
    print("\n" + "=" * 60)
    print("示例3: 批量写入邮件")
    print("=" * 60)
    
    # 创建大量测试邮件
    emails = []
    for i in range(150):
        email = EmailMessage(
            email_account="user@gmail.com",
            message_id=f"<batch{i}@mail.gmail.com>",
            subject=f"批量测试邮件 #{i+1}",
            date=datetime.now(),
            from_address="sender@example.com",
            body_text=f"批量写入测试邮件 {i+1}"
        )
        emails.append(email)
    
    # 批量写入
    with CSVWriter(output_path="output/example3_batch.csv") as writer:
        success_count = writer.write_messages(emails)
        print(f"✓ 成功写入: {success_count}/{len(emails)} 封邮件")
        stats = writer.get_stats()
        print(f"✓ 文件大小: {stats['file_size']} 字节")


def example_4_with_attachments():
    """示例4: 包含附件的邮件"""
    print("\n" + "=" * 60)
    print("示例4: 写入包含附件的邮件")
    print("=" * 60)
    
    # 创建附件
    attachment1 = Attachment(
        filename="report.pdf",
        content_type="application/pdf",
        size=1024,
        content=b"fake pdf content"
    )
    
    attachment2 = Attachment(
        filename="image.png",
        content_type="image/png",
        size=2048,
        content=b"fake image content"
    )
    
    # 创建带附件的邮件
    email = EmailMessage(
        email_account="user@gmail.com",
        message_id="<attach@mail.gmail.com>",
        subject="包含附件的邮件",
        date=datetime.now(),
        from_address="sender@example.com",
        from_name="发件人",
        body_text="请查看附件中的报告和图片。",
        attachments=[attachment1, attachment2]
    )
    
    with CSVWriter(output_path="output/example4_attachments.csv") as writer:
        writer.write_message(email)
        print(f"✓ 邮件已写入")
        print(f"  - 附件数量: {len(email.attachments)}")
        print(f"  - 附件名称: {email.get_attachment_names()}")


def example_5_append_mode():
    """示例5: 追加模式"""
    print("\n" + "=" * 60)
    print("示例5: 追加模式")
    print("=" * 60)
    
    output_path = "output/example5_append.csv"
    
    # 第一次写入
    email1 = EmailMessage(
        email_account="user@gmail.com",
        message_id="<first@mail.gmail.com>",
        subject="第一封邮件",
        date=datetime.now(),
        from_address="sender@example.com",
        body_text="这是第一次写入的邮件。"
    )
    
    writer = CSVWriter(output_path=output_path)
    writer.open(append=False)  # 覆盖模式
    writer.write_message(email1)
    writer.close()
    print(f"✓ 第一次写入完成: 1封邮件")
    
    # 第二次写入(追加)
    email2 = EmailMessage(
        email_account="user@gmail.com",
        message_id="<second@mail.gmail.com>",
        subject="第二封邮件",
        date=datetime.now(),
        from_address="sender@example.com",
        body_text="这是追加写入的邮件。"
    )
    
    writer = CSVWriter(output_path=output_path)
    writer.open(append=True)  # 追加模式
    writer.write_message(email2)
    writer.close()
    print(f"✓ 追加写入完成: 1封邮件")
    print(f"✓ 文件路径: {output_path}")


def example_6_with_config():
    """示例6: 使用配置管理器"""
    print("\n" + "=" * 60)
    print("示例6: 使用配置管理器")
    print("=" * 60)
    
    # 创建配置管理器
    config = ConfigManager()
    
    # 创建测试邮件
    email = EmailMessage(
        email_account="user@gmail.com",
        message_id="<config@mail.gmail.com>",
        subject="使用配置的邮件",
        date=datetime.now(),
        from_address="sender@example.com",
        body_text="这封邮件使用了配置管理器。"
    )
    
    # 使用配置创建写入器
    with CSVWriter(config_manager=config) as writer:
        writer.write_message(email)
        print(f"✓ 邮件已写入")
        print(f"✓ 输出路径: {writer.output_path}")


def example_7_error_handling():
    """示例7: 错误处理"""
    print("\n" + "=" * 60)
    print("示例7: 错误处理")
    print("=" * 60)
    
    # 测试1: 写入前未打开文件
    try:
        writer = CSVWriter(output_path="output/example7.csv")
        email = EmailMessage(
            email_account="user@gmail.com",
            message_id="<test@mail.gmail.com>",
            subject="测试",
            date=datetime.now(),
            from_address="sender@example.com"
        )
        writer.write_message(email)  # 应该抛出异常
    except CSVWriteError as e:
        print(f"✓ 正确捕获错误: {e}")
    
    # 测试2: 无效参数类型
    try:
        with CSVWriter(output_path="output/example7.csv") as writer:
            writer.write_message("invalid")  # 应该抛出TypeError
    except TypeError as e:
        print(f"✓ 正确捕获类型错误: {e}")


def example_8_factory_function():
    """示例8: 使用工厂函数"""
    print("\n" + "=" * 60)
    print("示例8: 使用工厂函数 create_csv_writer")
    print("=" * 60)
    
    emails = [
        EmailMessage(
            email_account="user@gmail.com",
            message_id=f"<factory{i}@mail.gmail.com>",
            subject=f"工厂函数测试 #{i+1}",
            date=datetime.now(),
            from_address="sender@example.com",
            body_text=f"测试邮件 {i+1}"
        )
        for i in range(5)
    ]
    
    # 使用工厂函数
    with create_csv_writer(output_path="output/example8_factory.csv") as writer:
        writer.write_messages(emails)
        print(f"✓ 已写入 {len(emails)} 封邮件")


def example_9_special_characters():
    """示例9: 特殊字符处理"""
    print("\n" + "=" * 60)
    print("示例9: 特殊字符处理")
    print("=" * 60)
    
    # 创建包含特殊字符的邮件
    email = EmailMessage(
        email_account="user@gmail.com",
        message_id="<special@mail.gmail.com>",
        subject='测试主题: "引号", 逗号,换行符',
        date=datetime.now(),
        from_address="sender@example.com",
        from_name="发件人 <特殊>",
        to_addresses=["user1@example.com", "user2@example.com"],
        cc_addresses=["cc1@example.com"],
        body_text="正文包含:\n- 换行符\n- 逗号,分号;\n- \"引号\"\n- 其他特殊字符: <>&",
        labels=["重要", "工作", "项目A"]
    )
    
    with CSVWriter(output_path="output/example9_special.csv") as writer:
        writer.write_message(email)
        print(f"✓ 特殊字符邮件已写入")
        print(f"✓ CSV库会自动处理引号和逗号的转义")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("CSV写入器使用示例")
    print("=" * 60)
    
    try:
        example_1_basic_usage()
        example_2_context_manager()
        example_3_batch_write()
        example_4_with_attachments()
        example_5_append_mode()
        example_6_with_config()
        example_7_error_handling()
        example_8_factory_function()
        example_9_special_characters()
        
        print("\n" + "=" * 60)
        print("✓ 所有示例执行完成!")
        print("✓ 请检查 output/ 目录查看生成的CSV文件")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()