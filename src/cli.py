#!/usr/bin/env python3
"""
CLI命令行接口模块

提供完整的命令行参数解析和验证功能。
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

__version__ = '1.0.0'
__author__ = 'Email Connector Team'
__description__ = 'IMAP邮件提取和CSV导出工具'


def parse_args(args=None):
    """
    解析命令行参数
    
    Args:
        args: 命令行参数列表(用于测试),None时使用sys.argv
        
    Returns:
        argparse.Namespace: 解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        prog='email-connector',
        description=f'{__description__} v{__version__}',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s --unseen --limit 10
  %(prog)s --from-date 2024-01-01 --to-date 2024-01-31
  %(prog)s --output emails.csv --save-attachments ./attachments
  %(prog)s --sender "boss@company.com" --subject "report"
  %(prog)s -v --debug --dry-run

配置文件:
  程序默认从.env文件读取邮箱账号和密码
  使用--config参数可指定其他配置文件路径
        """
    )
    
    # 版本信息
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    # 连接参数组
    conn_group = parser.add_argument_group('连接参数')
    conn_group.add_argument(
        '--host',
        type=str,
        help='IMAP服务器地址(默认从配置读取)'
    )
    conn_group.add_argument(
        '--port',
        type=int,
        help='IMAP端口号(默认993)'
    )
    conn_group.add_argument(
        '--no-ssl',
        action='store_true',
        help='禁用SSL连接(默认启用SSL)'
    )
    conn_group.add_argument(
        '--timeout',
        type=int,
        help='连接超时秒数(默认30秒)'
    )
    
    # 认证参数组
    auth_group = parser.add_argument_group('认证参数')
    auth_group.add_argument(
        '--email',
        type=str,
        help='邮箱账号(可从.env读取)'
    )
    auth_group.add_argument(
        '--password',
        type=str,
        help='邮箱密码或应用专用密码(可从.env读取)'
    )
    
    # 筛选参数组
    filter_group = parser.add_argument_group('筛选参数')
    filter_group.add_argument(
        '--folder',
        type=str,
        default='INBOX',
        help='邮箱文件夹名称(默认: INBOX)'
    )
    filter_group.add_argument(
        '--limit',
        type=int,
        help='限制获取的邮件数量'
    )
    filter_group.add_argument(
        '--from-date',
        type=str,
        dest='from_date',
        help='开始日期,格式: YYYY-MM-DD'
    )
    filter_group.add_argument(
        '--to-date',
        type=str,
        dest='to_date',
        help='结束日期,格式: YYYY-MM-DD'
    )
    filter_group.add_argument(
        '--sender',
        type=str,
        help='发件人邮箱地址或名称过滤'
    )
    filter_group.add_argument(
        '--subject',
        type=str,
        help='邮件主题关键词过滤'
    )
    filter_group.add_argument(
        '--unseen',
        action='store_true',
        help='只获取未读邮件'
    )
    
    # 输出参数组
    output_group = parser.add_argument_group('输出参数')
    output_group.add_argument(
        '--output',
        type=str,
        help='CSV输出文件路径(默认: output/csv/emails_<timestamp>.csv)'
    )
    output_group.add_argument(
        '--save-attachments',
        type=str,
        dest='save_attachments',
        metavar='DIR',
        help='保存附件到指定目录'
    )
    output_group.add_argument(
        '--mark-as-read',
        action='store_true',
        dest='mark_as_read',
        help='处理后标记邮件为已读'
    )
    
    # 其他参数组
    other_group = parser.add_argument_group('其他参数')
    other_group.add_argument(
        '--config',
        type=str,
        default='.env',
        help='配置文件路径(默认: .env)'
    )
    other_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细日志输出'
    )
    other_group.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式(更详细的日志)'
    )
    other_group.add_argument(
        '--dry-run',
        action='store_true',
        dest='dry_run',
        help='模拟运行,不实际写入文件'
    )
    
    # 解析参数
    parsed_args = parser.parse_args(args)
    
    # 验证参数
    validate_args(parsed_args, parser)
    
    return parsed_args


def validate_args(args, parser):
    """
    验证参数有效性
    
    Args:
        args: 解析后的参数对象
        parser: ArgumentParser对象,用于报错
        
    Raises:
        SystemExit: 参数验证失败时退出
    """
    # 验证日期格式
    if args.from_date:
        try:
            datetime.strptime(args.from_date, '%Y-%m-%d')
        except ValueError:
            parser.error(f"无效的开始日期格式: {args.from_date}, 应为 YYYY-MM-DD")
    
    if args.to_date:
        try:
            datetime.strptime(args.to_date, '%Y-%m-%d')
        except ValueError:
            parser.error(f"无效的结束日期格式: {args.to_date}, 应为 YYYY-MM-DD")
    
    # 验证日期范围
    if args.from_date and args.to_date:
        from_date = datetime.strptime(args.from_date, '%Y-%m-%d')
        to_date = datetime.strptime(args.to_date, '%Y-%m-%d')
        if from_date > to_date:
            parser.error("开始日期不能晚于结束日期")
    
    # 验证端口范围
    if args.port is not None:
        if not (1 <= args.port <= 65535):
            parser.error(f"无效的端口号: {args.port}, 应在 1-65535 之间")
    
    # 验证超时时间
    if args.timeout is not None:
        if args.timeout <= 0:
            parser.error(f"无效的超时时间: {args.timeout}, 应为正整数")
    
    # 验证邮件数量限制
    if args.limit is not None:
        if args.limit <= 0:
            parser.error(f"无效的邮件数量限制: {args.limit}, 应为正整数")
    
    # 验证配置文件路径
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"警告: 配置文件不存在: {args.config}", file=sys.stderr)
    
    # 验证输出路径(如果是目录,需要存在)
    if args.output:
        output_path = Path(args.output)
        if output_path.suffix == '':  # 是目录
            if not output_path.exists():
                parser.error(f"输出目录不存在: {args.output}")
    
    # 验证附件目录
    if args.save_attachments:
        attach_dir = Path(args.save_attachments)
        # 不要求目录已存在,程序会自动创建


def get_filter_criteria(args):
    """
    从CLI参数构建筛选条件字典
    
    Args:
        args: 解析后的参数对象
        
    Returns:
        dict: 筛选条件字典
    """
    criteria = {}
    
    if args.from_date:
        criteria['from_date'] = args.from_date
    
    if args.to_date:
        criteria['to_date'] = args.to_date
    
    if args.sender:
        criteria['sender'] = args.sender
    
    if args.subject:
        criteria['subject'] = args.subject
    
    if args.unseen:
        criteria['unseen'] = True
    
    if args.limit:
        criteria['limit'] = args.limit
    
    return criteria


def main():
    """CLI模块测试入口"""
    args = parse_args()
    
    print("=" * 60)
    print("CLI参数解析结果:")
    print("=" * 60)
    
    # 连接参数
    print("\n[连接参数]")
    print(f"  服务器地址: {args.host or '(从配置读取)'}")
    print(f"  端口号: {args.port or '(从配置读取)'}")
    print(f"  使用SSL: {not args.no_ssl}")
    print(f"  超时时间: {args.timeout or '(从配置读取)'} 秒")
    
    # 认证参数
    print("\n[认证参数]")
    print(f"  邮箱账号: {args.email or '(从配置读取)'}")
    print(f"  密码: {'***' if args.password else '(从配置读取)'}")
    
    # 筛选参数
    print("\n[筛选参数]")
    print(f"  邮箱文件夹: {args.folder}")
    print(f"  日期范围: {args.from_date or '不限'} ~ {args.to_date or '不限'}")
    print(f"  发件人: {args.sender or '不限'}")
    print(f"  主题关键词: {args.subject or '不限'}")
    print(f"  只看未读: {args.unseen}")
    print(f"  数量限制: {args.limit or '不限'}")
    
    # 输出参数
    print("\n[输出参数]")
    print(f"  CSV输出: {args.output or '(默认路径)'}")
    print(f"  保存附件: {args.save_attachments or '不保存'}")
    print(f"  标记已读: {args.mark_as_read}")
    
    # 其他参数
    print("\n[其他参数]")
    print(f"  配置文件: {args.config}")
    print(f"  详细输出: {args.verbose}")
    print(f"  调试模式: {args.debug}")
    print(f"  模拟运行: {args.dry_run}")
    
    # 筛选条件
    print("\n[筛选条件字典]")
    criteria = get_filter_criteria(args)
    for key, value in criteria.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✓ CLI参数解析成功")
    print("=" * 60)


if __name__ == '__main__':
    main()