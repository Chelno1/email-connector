"""
数据模型使用示例

本示例展示如何使用 EmailMessage 和 Attachment 数据模型:
1. 创建附件对象
2. 创建邮件消息对象
3. 添加附件到邮件
4. 转换为字典和CSV行格式
5. 从字典重建对象
6. 保存附件到磁盘
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import EmailMessage, Attachment


def example_1_create_attachment():
    """示例1: 创建附件对象"""
    print("=" * 60)
    print("示例1: 创建附件对象")
    print("=" * 60)
    
    # 创建PDF附件
    pdf_content = b"PDF file content..."
    pdf_attachment = Attachment(
        filename="report.pdf",
        content_type="application/pdf",
        size=len(pdf_content),
        content=pdf_content
    )
    
    print(f"附件对象: {pdf_attachment}")
    print(f"文件大小: {pdf_attachment.get_size_mb()} MB")
    print(f"文件扩展名: {pdf_attachment.get_extension()}")
    print(f"是否为图片: {pdf_attachment.is_image()}")
    print()


def example_2_create_email_message():
    """示例2: 创建邮件消息对象"""
    print("=" * 60)
    print("示例2: 创建邮件消息对象")
    print("=" * 60)
    
    # 创建邮件对象
    email = EmailMessage(
        email_account="user@gmail.com",
        message_id="<abc123@mail.gmail.com>",
        subject="项目进度报告",
        date=datetime(2024, 1, 15, 14, 30, 25),
        from_address="boss@company.com",
        from_name="张经理",
        to_addresses=["employee1@company.com", "employee2@company.com"],
        to_names=["李员工", "王员工"],
        cc_addresses=["hr@company.com"],
        body_text="请查看附件中的项目进度报告。",
        labels=["IMPORTANT", "WORK"]
    )
    
    print(f"邮件对象: {email}")
    print(f"发件人: {email.from_name} <{email.from_address}>")
    print(f"收件人数量: {len(email.to_addresses)}")
    print(f"标签: {', '.join(email.labels)}")
    print()


def example_3_add_attachments():
    """示例3: 添加附件到邮件"""
    print("=" * 60)
    print("示例3: 添加附件到邮件")
    print("=" * 60)
    
    # 创建邮件
    email = EmailMessage(
        email_account="user@gmail.com",
        message_id="<def456@mail.gmail.com>",
        subject="照片分享",
        date=datetime.now(),
        from_address="friend@example.com",
        from_name="好友"
    )
    
    # 创建并添加图片附件
    image1 = Attachment(
        filename="photo1.jpg",
        content_type="image/jpeg",
        size=2048576,  # 2MB
        content=b"Image content..."
    )
    
    image2 = Attachment(
        filename="photo2.png",
        content_type="image/png",
        size=1024000,  # 1MB
        content=b"PNG content..."
    )
    
    email.add_attachment(image1)
    email.add_attachment(image2)
    
    print(f"邮件对象: {email}")
    print(f"是否有附件: {email.has_attachment}")
    print(f"附件数量: {len(email.attachments)}")
    print(f"附件名称: {email.get_attachment_names()}")
    print()


def example_4_to_dict_and_csv():
    """示例4: 转换为字典和CSV行格式"""
    print("=" * 60)
    print("示例4: 转换为字典和CSV行格式")
    print("=" * 60)
    
    # 创建完整的邮件对象
    attachment = Attachment(
        filename="document.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        size=512000,
        content=b"Document content..."
    )
    
    email = EmailMessage(
        email_account="work@company.com",
        message_id="<ghi789@mail.company.com>",
        thread_id="thread-001",
        subject="会议纪要",
        date=datetime(2024, 1, 20, 10, 0, 0),
        from_address="secretary@company.com",
        from_name="秘书",
        to_addresses=["manager@company.com"],
        to_names=["经理"],
        cc_addresses=["assistant@company.com"],
        body_text="请查看本周会议纪要。",
        labels=["MEETING", "IMPORTANT"],
        is_read=False
    )
    email.add_attachment(attachment)
    
    # 转换为字典
    print("转换为字典:")
    email_dict = email.to_dict()
    for key, value in email_dict.items():
        if key not in ['body_text', 'body_html', 'attachments']:
            print(f"  {key}: {value}")
    print()
    
    # 转换为CSV行
    print("转换为CSV行格式:")
    csv_row = email.to_csv_row()
    for key, value in csv_row.items():
        if key != 'body_text':
            print(f"  {key}: {value}")
    print()


def example_5_from_dict():
    """示例5: 从字典重建对象"""
    print("=" * 60)
    print("示例5: 从字典重建对象")
    print("=" * 60)
    
    # 原始邮件数据(通常来自数据库或文件)
    data = {
        'email_account': 'restored@example.com',
        'message_id': '<restored123@mail.example.com>',
        'thread_id': 'thread-002',
        'subject': '恢复的邮件',
        'date': '2024-01-25T16:45:30',
        'from_address': 'sender@example.com',
        'from_name': '发送者',
        'to_addresses': ['receiver@example.com'],
        'to_names': ['接收者'],
        'cc_addresses': [],
        'body_text': '这是恢复的邮件内容。',
        'body_html': '<p>这是恢复的邮件内容。</p>',
        'has_attachment': True,
        'attachments': [
            {
                'filename': 'restored_file.pdf',
                'content_type': 'application/pdf',
                'size': 204800,
                'saved_path': '/path/to/restored_file.pdf'
            }
        ],
        'labels': ['ARCHIVED'],
        'is_read': True,
        'uid': 12345
    }
    
    # 从字典重建邮件对象
    restored_email = EmailMessage.from_dict(data)
    
    print(f"重建的邮件对象: {restored_email}")
    print(f"主题: {restored_email.subject}")
    print(f"日期: {restored_email.date}")
    print(f"附件: {restored_email.get_attachment_names()}")
    print(f"UID: {restored_email.uid}")
    print()


def example_6_save_attachments():
    """示例6: 保存附件到磁盘"""
    print("=" * 60)
    print("示例6: 保存附件到磁盘")
    print("=" * 60)
    
    # 创建测试附件
    test_content = b"This is a test file content for demonstration purposes."
    attachment = Attachment(
        filename="test_file.txt",
        content_type="text/plain",
        size=len(test_content),
        content=test_content
    )
    
    # 保存到临时目录
    output_dir = "./output/attachments/test"
    
    try:
        saved_path = attachment.save(output_dir)
        print(f"附件已保存到: {saved_path}")
        print(f"附件信息: {attachment}")
        
        # 验证文件是否存在
        if Path(saved_path).exists():
            print(f"✓ 文件保存成功")
            file_size = Path(saved_path).stat().st_size
            print(f"✓ 文件大小: {file_size} 字节")
        
    except Exception as e:
        print(f"✗ 保存失败: {e}")
    
    print()


def example_7_complete_workflow():
    """示例7: 完整工作流程"""
    print("=" * 60)
    print("示例7: 完整工作流程")
    print("=" * 60)
    
    # 1. 创建邮件和附件
    email = EmailMessage(
        email_account="workflow@example.com",
        message_id="<workflow@mail.example.com>",
        subject="完整工作流示例",
        date=datetime.now(),
        from_address="demo@example.com",
        from_name="演示账户",
        to_addresses=["recipient@example.com"],
        to_names=["接收者"],
        body_text="这是一个完整的工作流程示例。"
    )
    
    # 2. 创建多个附件
    attachments_data = [
        ("report.pdf", "application/pdf", b"PDF report content"),
        ("chart.png", "image/png", b"PNG chart content"),
        ("data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", b"Excel data")
    ]
    
    for filename, content_type, content in attachments_data:
        att = Attachment(
            filename=filename,
            content_type=content_type,
            size=len(content),
            content=content
        )
        email.add_attachment(att)
    
    # 3. 转换为CSV格式
    csv_row = email.to_csv_row()
    print("CSV行数据:")
    for key in ['subject', 'from', 'to', 'date', 'attachment_count', 'attachment_names']:
        print(f"  {key}: {csv_row[key]}")
    
    # 4. 保存所有附件
    print("\n保存附件:")
    output_dir = "./output/attachments/workflow"
    for att in email.attachments:
        try:
            saved_path = att.save(output_dir)
            print(f"  ✓ {att.filename} -> {saved_path}")
        except Exception as e:
            print(f"  ✗ {att.filename} 保存失败: {e}")
    
    # 5. 序列化和反序列化
    print("\n序列化测试:")
    email_dict = email.to_dict()
    print(f"  原始邮件: {email}")
    
    restored = EmailMessage.from_dict(email_dict)
    print(f"  恢复邮件: {restored}")
    print(f"  ✓ 序列化/反序列化成功")
    
    print()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("数据模型使用示例")
    print("=" * 60 + "\n")
    
    try:
        example_1_create_attachment()
        example_2_create_email_message()
        example_3_add_attachments()
        example_4_to_dict_and_csv()
        example_5_from_dict()
        example_6_save_attachments()
        example_7_complete_workflow()
        
        print("=" * 60)
        print("所有示例运行完成!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()