"""
邮件解析器使用示例

演示EmailParser的各种功能:
- 解析单封邮件
- 批量解析邮件
- 提取附件
- 处理不同编码的邮件
- 处理multipart邮件
- 错误处理
"""

import email
from email import policy
from datetime import datetime
from src.core.email_parser import EmailParser, EmailParseError


def example_1_parse_simple_email():
    """示例1: 解析简单邮件"""
    print("\n=== 示例1: 解析简单邮件 ===")
    
    # 创建一个简单的测试邮件
    raw_email = b"""From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 15 Jan 2024 14:30:00 +0800
Message-ID: <test123@example.com>
Content-Type: text/plain; charset=utf-8

This is a test email body.
"""
    
    # 创建解析器
    parser = EmailParser("user@gmail.com")
    
    # 解析邮件
    try:
        msg = parser.parse(raw_email, uid=1)
        
        print(f"消息ID: {msg.message_id}")
        print(f"主题: {msg.subject}")
        print(f"发件人: {msg.from_address}")
        print(f"发件人名称: {msg.from_name}")
        print(f"日期: {msg.date}")
        print(f"正文: {msg.body_text}")
        print(f"是否有附件: {msg.has_attachment}")
        
    except EmailParseError as e:
        print(f"解析失败: {e}")


def example_2_parse_chinese_email():
    """示例2: 解析中文邮件"""
    print("\n=== 示例2: 解析中文邮件 ===")
    
    # 创建包含中文的邮件(使用编码后的Base64)
    raw_email = b"""From: =?UTF-8?B?5byg5LiJ?= <zhangsan@example.com>
To: lisi@example.com
Subject: =?UTF-8?B?5rWL6K+V6YKu5Lu2?=
Date: Mon, 15 Jan 2024 14:30:00 +0800
Content-Type: text/plain; charset=utf-8

""" + "这是一封测试邮件。\n包含中文内容。\n".encode('utf-8')
    
    parser = EmailParser("user@gmail.com")
    
    try:
        msg = parser.parse(raw_email)
        
        print(f"主题: {msg.subject}")
        print(f"发件人: {msg.from_name} <{msg.from_address}>")
        print(f"正文: {msg.body_text}")
        
    except EmailParseError as e:
        print(f"解析失败: {e}")


def example_3_parse_multipart_email():
    """示例3: 解析multipart邮件(纯文本+HTML)"""
    print("\n=== 示例3: 解析multipart邮件 ===")
    
    # 创建multipart邮件
    raw_email = b"""From: sender@example.com
To: recipient@example.com
Subject: Multipart Email
Date: Mon, 15 Jan 2024 14:30:00 +0800
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset=utf-8

This is the plain text version.

--boundary123
Content-Type: text/html; charset=utf-8

<html>
<body>
<h1>This is the HTML version</h1>
<p>With <strong>formatting</strong>.</p>
</body>
</html>

--boundary123--
"""
    
    parser = EmailParser("user@gmail.com")
    
    try:
        msg = parser.parse(raw_email)
        
        print(f"主题: {msg.subject}")
        print(f"纯文本正文: {msg.body_text}")
        print(f"HTML正文长度: {len(msg.body_html) if msg.body_html else 0}")
        
    except EmailParseError as e:
        print(f"解析失败: {e}")


def example_4_parse_email_with_attachment():
    """示例4: 解析带附件的邮件"""
    print("\n=== 示例4: 解析带附件的邮件 ===")
    
    # 创建带附件的邮件
    raw_email = b"""From: sender@example.com
To: recipient@example.com
Subject: Email with Attachment
Date: Mon, 15 Jan 2024 14:30:00 +0800
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset=utf-8

Please see the attached file.

--boundary123
Content-Type: application/pdf; name="document.pdf"
Content-Disposition: attachment; filename="document.pdf"
Content-Transfer-Encoding: base64

JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwo+PgplbmRvYmoKc3RhcnR4
cmVmCjEwOQolJUVPRgo=

--boundary123--
"""
    
    parser = EmailParser("user@gmail.com")
    
    try:
        msg = parser.parse(raw_email)
        
        print(f"主题: {msg.subject}")
        print(f"是否有附件: {msg.has_attachment}")
        print(f"附件数量: {len(msg.attachments)}")
        
        for att in msg.attachments:
            print(f"\n附件信息:")
            print(f"  文件名: {att.filename}")
            print(f"  类型: {att.content_type}")
            print(f"  大小: {att.get_size_mb()} MB")
            print(f"  是否图片: {att.is_image()}")
            
    except EmailParseError as e:
        print(f"解析失败: {e}")


def example_5_batch_parse():
    """示例5: 批量解析邮件"""
    print("\n=== 示例5: 批量解析邮件 ===")
    
    # 创建多封测试邮件
    emails = [
        (1, b"""From: sender1@example.com
To: recipient@example.com
Subject: Email 1
Date: Mon, 15 Jan 2024 14:30:00 +0800
Content-Type: text/plain

Email 1 body
"""),
        (2, b"""From: sender2@example.com
To: recipient@example.com
Subject: Email 2
Date: Mon, 15 Jan 2024 14:31:00 +0800
Content-Type: text/plain

Email 2 body
"""),
        (3, b"""From: sender3@example.com
To: recipient@example.com
Subject: Email 3
Date: Mon, 15 Jan 2024 14:32:00 +0800
Content-Type: text/plain

Email 3 body
"""),
    ]
    
    parser = EmailParser("user@gmail.com")
    
    # 批量解析
    print("开始批量解析...")
    for msg in parser.parse_batch(emails):
        print(f"- UID={msg.uid}, 主题={msg.subject}, 发件人={msg.from_address}")


def example_6_parse_multiple_recipients():
    """示例6: 解析多收件人邮件"""
    print("\n=== 示例6: 解析多收件人邮件 ===")
    
    raw_email = b"""From: sender@example.com
To: recipient1@example.com, recipient2@example.com, recipient3@example.com
Cc: cc1@example.com, cc2@example.com
Subject: Multiple Recipients
Date: Mon, 15 Jan 2024 14:30:00 +0800
Content-Type: text/plain

Email to multiple recipients.
"""
    
    parser = EmailParser("user@gmail.com")
    
    try:
        msg = parser.parse(raw_email)
        
        print(f"主题: {msg.subject}")
        print(f"收件人数量: {len(msg.to_addresses)}")
        print(f"收件人列表:")
        for addr in msg.to_addresses:
            print(f"  - {addr}")
        
        print(f"抄送数量: {len(msg.cc_addresses)}")
        print(f"抄送列表:")
        for addr in msg.cc_addresses:
            print(f"  - {addr}")
            
    except EmailParseError as e:
        print(f"解析失败: {e}")


def example_7_error_handling():
    """示例7: 错误处理"""
    print("\n=== 示例7: 错误处理 ===")
    
    # 测试无效邮件
    invalid_emails = [
        b"",  # 空邮件
        b"This is not a valid email",  # 无效格式
    ]
    
    parser = EmailParser("user@gmail.com")
    
    for i, raw_email in enumerate(invalid_emails, 1):
        try:
            msg = parser.parse(raw_email)
            print(f"邮件{i}: 解析成功")
        except EmailParseError as e:
            print(f"邮件{i}: 解析失败 - {e}")


def example_8_save_attachments():
    """示例8: 保存附件"""
    print("\n=== 示例8: 保存附件 ===")
    
    # 创建带附件的邮件
    raw_email = b"""From: sender@example.com
To: recipient@example.com
Subject: Email with Text Attachment
Date: Mon, 15 Jan 2024 14:30:00 +0800
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset=utf-8

Please see the attached file.

--boundary123
Content-Type: text/plain; name="readme.txt"
Content-Disposition: attachment; filename="readme.txt"

This is the content of the attachment.
It's a simple text file.

--boundary123--
"""
    
    parser = EmailParser("user@gmail.com")
    
    try:
        msg = parser.parse(raw_email)
        
        print(f"主题: {msg.subject}")
        print(f"附件数量: {len(msg.attachments)}")
        
        # 保存附件
        output_dir = "./output/attachments/test"
        for att in msg.attachments:
            try:
                saved_path = att.save(output_dir)
                print(f"附件已保存: {saved_path}")
            except Exception as e:
                print(f"保存附件失败: {e}")
                
    except EmailParseError as e:
        print(f"解析失败: {e}")


def example_9_csv_format():
    """示例9: CSV格式输出"""
    print("\n=== 示例9: CSV格式输出 ===")
    
    raw_email = b"""From: =?UTF-8?B?5byg5LiJ?= <zhangsan@example.com>
To: lisi@example.com
Subject: =?UTF-8?B?5rWL6K+V6YKu5Lu2?=
Date: Mon, 15 Jan 2024 14:30:00 +0800
Content-Type: text/plain; charset=utf-8

""" + "这是邮件正文。\n".encode('utf-8')
    
    parser = EmailParser("user@gmail.com")
    
    try:
        msg = parser.parse(raw_email)
        
        # 转换为CSV行格式
        csv_row = msg.to_csv_row()
        
        print("CSV格式数据:")
        for key, value in csv_row.items():
            print(f"  {key}: {value}")
            
    except EmailParseError as e:
        print(f"解析失败: {e}")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("邮件解析器使用示例")
    print("=" * 60)
    
    example_1_parse_simple_email()
    example_2_parse_chinese_email()
    example_3_parse_multipart_email()
    example_4_parse_email_with_attachment()
    example_5_batch_parse()
    example_6_parse_multiple_recipients()
    example_7_error_handling()
    example_8_save_attachments()
    example_9_csv_format()
    
    print("\n" + "=" * 60)
    print("所有示例执行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()