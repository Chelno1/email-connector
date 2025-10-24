#!/usr/bin/env python3
"""
主程序模块

协调各模块工作流程,实现完整的邮件提取和CSV导出功能。
"""

import sys
import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
import logging

from src.utils.config_manager import ConfigManager
from src.utils.logger import setup_logging, get_logger, log_performance
from src.core.imap_client import IMAPClient, IMAPConnectionError, IMAPAuthenticationError
from src.core.email_parser import EmailParser, EmailParseError
from src.core.csv_writer import CSVWriter, CSVWriteError
from src.models.email_message import EmailMessage


class EmailConnector:
    """邮件连接器主类"""
    
    def __init__(self, config: ConfigManager):
        """
        初始化邮件连接器
        
        Args:
            config: 配置管理器实例
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.stats = {
            'searched': 0,
            'fetched': 0,
            'parsed': 0,
            'failed': 0,
            'saved': 0,
            'attachments': 0,
            'start_time': None,
            'end_time': None
        }
    
    @log_performance
    def run(self, args) -> int:
        """
        运行主程序流程
        
        Args:
            args: CLI参数对象
            
        Returns:
            int: 退出码(0=成功, 1=失败)
        """
        try:
            self.stats['start_time'] = datetime.now()
            
            self.logger.info("=" * 60)
            self.logger.info("启动Email Connector - IMAP邮件提取程序")
            self.logger.info("=" * 60)
            
            # 1. 合并CLI参数到配置
            self._merge_cli_args(args)
            
            # 2. 显示运行配置
            self._display_config(args)
            
            # 3. 如果是dry-run模式,只显示配置
            if args.dry_run:
                self.logger.info("\n[模拟运行模式] 不会实际连接IMAP或写入文件")
                self.logger.info("=" * 60)
                return 0
            
            # 4. 连接IMAP并处理邮件
            emails = self._process_emails(args)
            
            # 5. 保存到CSV
            if emails:
                self._save_to_csv(emails, args)
                
                # 6. 保存附件(默认启用,除非明确禁用)
                if not getattr(args, 'no_attachments', False):
                    # 从CLI参数或配置获取附件目录
                    attach_dir = getattr(args, 'attachment_dir', None)
                    if not attach_dir:
                        output_config = self.config.get_output_config()
                        attach_dir = output_config['attachment_dir']
                    
                    if attach_dir:
                        self._save_attachments(emails, attach_dir)
            else:
                self.logger.warning("没有找到符合条件的邮件")
            
            # 7. 输出统计信息
            self.stats['end_time'] = datetime.now()
            self._print_statistics()
            
            self.logger.info("=" * 60)
            self.logger.info("✓ 程序执行成功")
            self.logger.info("=" * 60)
            
            return 0
            
        except KeyboardInterrupt:
            self.logger.warning("\n\n用户中断程序执行")
            return 130
            
        except Exception as e:
            self.logger.error(f"程序执行失败: {e}", exc_info=True)
            return 1
    
    def _merge_cli_args(self, args):
        """
        合并CLI参数到配置
        
        配置优先级: CLI参数 > 环境变量 > 配置文件
        
        Args:
            args: CLI参数对象
        """
        self.logger.debug("合并CLI参数到配置...")
        
        # ConfigManager已经在初始化时接收了cli_args
        # 通过config.cli_args来传递命令行参数
        # 这里不需要额外操作,因为ConfigManager.get()会自动检查cli_args
        
        # 更新cli_args字典以支持ConfigManager的优先级查找
        if args.host:
            self.config.cli_args['host'] = args.host
        if args.port:
            self.config.cli_args['port'] = args.port
        if args.no_ssl:
            self.config.cli_args['use-ssl'] = False
        if args.timeout:
            self.config.cli_args['timeout'] = args.timeout
        if args.email:
            self.config.cli_args['email'] = args.email
        if args.password:
            self.config.cli_args['password'] = args.password
    
    def _display_config(self, args):
        """
        显示运行配置
        
        Args:
            args: CLI参数对象
        """
        self.logger.info("\n[运行配置]")
        
        # 连接配置
        email = self.config.get_email_credentials()[0]
        imap_config = self.config.get_imap_config()
        host = imap_config['host']
        port = imap_config['port']
        use_ssl = imap_config['use_ssl']
        
        self.logger.info(f"  邮箱账户: {email}")
        self.logger.info(f"  IMAP服务器: {host}:{port} (SSL: {use_ssl})")
        self.logger.info(f"  邮箱文件夹: {args.folder}")
        
        # 筛选条件
        filters = []
        if args.from_date:
            filters.append(f"起始日期: {args.from_date}")
        if args.to_date:
            filters.append(f"结束日期: {args.to_date}")
        if args.sender:
            filters.append(f"发件人: {args.sender}")
        if args.subject:
            filters.append(f"主题: {args.subject}")
        if args.unseen:
            filters.append("只看未读")
        if args.limit:
            filters.append(f"数量限制: {args.limit}")
        
        if filters:
            self.logger.info(f"  筛选条件: {', '.join(filters)}")
        else:
            self.logger.info("  筛选条件: 无(获取所有邮件)")
        
        # 输出配置
        custom_filename = getattr(args, 'filename', None)
        output = args.output or self._get_default_output_path(custom_filename)
        self.logger.info(f"  CSV输出: {output}")
        
        # 显示附件配置
        if not getattr(args, 'no_attachments', False):
            attach_dir = getattr(args, 'attachment_dir', None)
            if not attach_dir:
                output_config = self.config.get_output_config()
                attach_dir = output_config['attachment_dir']
            self.logger.info(f"  附件保存: {attach_dir}")
        else:
            self.logger.info("  附件保存: 禁用")
        
        if args.mark_as_read:
            self.logger.info("  处理后标记为已读: 是")
        
        self.logger.info("")
    
    @log_performance
    def _process_emails(self, args) -> List[EmailMessage]:
        """
        处理邮件:连接、搜索、获取、解析
        
        Args:
            args: CLI参数对象
            
        Returns:
            List[EmailMessage]: 解析后的邮件列表
        """
        emails = []
        
        # 创建IMAP客户端
        client = IMAPClient(self.config)
        
        try:
            # 1. 连接和登录
            self.logger.info("正在连接IMAP服务器...")
            client.connect()
            
            email, password = self.config.get_email_credentials()
            self.logger.info("正在登录邮箱...")
            client.login(email, password)
            
            # 2. 选择文件夹
            self.logger.info(f"正在选择文件夹: {args.folder}")
            client.select_folder(args.folder)
            
            # 3. 搜索邮件
            self.logger.info("正在搜索邮件...")
            uids = self._search_emails(client, args)
            self.stats['searched'] = len(uids)
            
            if not uids:
                self.logger.warning("未找到符合条件的邮件")
                return emails
            
            self.logger.info(f"找到 {len(uids)} 封符合条件的邮件")
            
            # 4. 应用数量限制
            if args.limit and len(uids) > args.limit:
                self.logger.info(f"应用数量限制,只处理最新 {args.limit} 封邮件")
                uids = uids[-args.limit:]  # 获取最新的N封(列表末尾)
            
            # 5. 批量获取和解析
            self.logger.info("正在获取和解析邮件...")
            emails = self._fetch_and_parse(client, uids, email)
            
            # 6. 标记为已读(可选)
            if args.mark_as_read and emails:
                self.logger.info("正在标记邮件为已读...")
                read_uids = [uid for uid in uids[:len(emails)]]
                client.mark_as_read(read_uids)
            
        except IMAPConnectionError as e:
            self.logger.error(f"IMAP连接失败: {e}")
            raise
        except IMAPAuthenticationError as e:
            self.logger.error(f"IMAP认证失败: {e}")
            self.logger.error("请检查邮箱账号和密码是否正确")
            raise
        finally:
            # 7. 断开连接
            try:
                client.disconnect()
                self.logger.info("已断开IMAP连接")
            except:
                pass
        
        return emails
    
    def _search_emails(self, client: IMAPClient, args) -> List[int]:
        """
        搜索邮件
        
        Args:
            client: IMAP客户端
            args: CLI参数对象
            
        Returns:
            List[int]: 邮件UID列表
        """
        # 构建搜索条件
        criteria = []
        
        if args.from_date:
            criteria.append(f'SINCE {self._format_imap_date(args.from_date)}')
        
        if args.to_date:
            criteria.append(f'BEFORE {self._format_imap_date(args.to_date)}')
        
        if args.sender:
            criteria.append(f'FROM "{args.sender}"')
        
        if args.subject:
            criteria.append(f'SUBJECT "{args.subject}"')
        
        if args.unseen:
            criteria.append('UNSEEN')
        
        # 如果没有任何条件,搜索所有
        search_str = ' '.join(criteria) if criteria else 'ALL'
        
        self.logger.debug(f"IMAP搜索条件: {search_str}")
        
        return client.search_messages(folder=args.folder, criteria=search_str)
    
    def _format_imap_date(self, date_str: str) -> str:
        """
        格式化日期为IMAP格式
        
        Args:
            date_str: YYYY-MM-DD格式的日期
            
        Returns:
            str: DD-Mon-YYYY格式的日期
        """
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%d-%b-%Y')
    
    @log_performance
    def _fetch_and_parse(self, client: IMAPClient, uids: List[int], 
                         email_account: str) -> List[EmailMessage]:
        """
        批量获取和解析邮件
        
        Args:
            client: IMAP客户端
            uids: 邮件UID列表
            email_account: 邮箱账户
            
        Returns:
            List[EmailMessage]: 解析后的邮件列表
        """
        emails = []
        parser = EmailParser(email_account)
        
        total = len(uids)
        
        for i, (uid, raw_email) in enumerate(client.fetch_messages_batch(uids), 1):
            try:
                # 解析邮件
                email_msg = parser.parse(raw_email)
                emails.append(email_msg)
                
                self.stats['fetched'] += 1
                self.stats['parsed'] += 1
                
                # 统计附件
                if email_msg.attachments:
                    self.stats['attachments'] += len(email_msg.attachments)
                
                # 显示进度
                if i % 10 == 0 or i == total:
                    self.logger.info(f"  进度: {i}/{total} ({i*100//total}%)")
                
            except EmailParseError as e:
                self.logger.warning(f"解析邮件失败 (UID {uid}): {e}")
                self.stats['failed'] += 1
                continue
            except Exception as e:
                self.logger.error(f"处理邮件时出错 (UID {uid}): {e}")
                self.stats['failed'] += 1
                continue
        
        self.logger.info(f"成功解析 {len(emails)} 封邮件")
        
        return emails
    
    @log_performance
    def _save_to_csv(self, emails: List[EmailMessage], args):
        """
        保存邮件到CSV
        
        Args:
            emails: 邮件消息列表
            args: CLI参数对象
        """
        # 确定输出路径
        custom_filename = getattr(args, 'filename', None)
        output_path = args.output or self._get_default_output_path(custom_filename)
        
        # 确保输出目录存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"正在保存到CSV: {output_path}")
        
        try:
            with CSVWriter(str(output_path)) as writer:
                writer.write_messages(emails)
                stats = writer.get_stats()
                self.stats['saved'] = stats['write_count']
            
            self.logger.info(f"✓ 成功保存 {self.stats['saved']} 封邮件到CSV")
            
        except CSVWriteError as e:
            self.logger.error(f"CSV写入失败: {e}")
            raise
    
    @log_performance
    def _save_attachments(self, emails: List[EmailMessage], attach_dir: str):
        """
        保存附件
        
        Args:
            emails: 邮件消息列表
            attach_dir: 附件保存目录
        """
        attach_path = Path(attach_dir)
        attach_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"正在保存附件到: {attach_dir}")
        
        saved_count = 0
        
        for email in emails:
            if not email.attachments:
                continue
            
            # 为每封邮件创建子目录(使用日期)
            email_date = email.date.strftime('%Y%m%d')
            email_dir = attach_path / email_date
            email_dir.mkdir(exist_ok=True)
            
            for attachment in email.attachments:
                try:
                    # 保存附件
                    saved_path = attachment.save(str(email_dir))
                    saved_count += 1
                    self.logger.debug(f"  保存附件: {attachment.filename}")
                except Exception as e:
                    self.logger.warning(f"保存附件失败 ({attachment.filename}): {e}")
        
        self.logger.info(f"✓ 成功保存 {saved_count} 个附件")
    
    def _get_default_output_path(self, custom_filename: str = None) -> str:
        """
        获取默认输出路径
        
        Args:
            custom_filename: 自定义文件名(可选)
        
        Returns:
            str: 默认CSV输出路径
        """
        output_config = self.config.get_output_config()
        output_dir = output_config['csv_dir']
        
        if custom_filename:
            # 如果提供了自定义文件名，确保有.csv扩展名
            if not custom_filename.endswith('.csv'):
                custom_filename += '.csv'
            filename = custom_filename
        else:
            # 使用时间戳生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"emails_{timestamp}.csv"
        
        return str(Path(output_dir) / filename)
    
    def _print_statistics(self):
        """输出统计信息"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("执行统计")
        self.logger.info("=" * 60)
        
        # 计算耗时
        duration = self.stats['end_time'] - self.stats['start_time']
        
        self.logger.info(f"  搜索到的邮件: {self.stats['searched']} 封")
        self.logger.info(f"  获取的邮件: {self.stats['fetched']} 封")
        self.logger.info(f"  成功解析: {self.stats['parsed']} 封")
        self.logger.info(f"  解析失败: {self.stats['failed']} 封")
        self.logger.info(f"  保存到CSV: {self.stats['saved']} 封")
        self.logger.info(f"  附件总数: {self.stats['attachments']} 个")
        self.logger.info(f"  总耗时: {duration.total_seconds():.2f} 秒")


def main():
    """主程序入口"""
    from src.cli import parse_args
    
    # 1. 解析CLI参数
    args = parse_args()
    
    # 2. 将CLI参数转换为字典
    cli_args_dict = vars(args)
    
    # 3. 加载配置(传入CLI参数)
    config = ConfigManager(env_path=args.config, cli_args=cli_args_dict)
    
    # 4. 设置日志(setup_logging会从config读取日志级别)
    setup_logging(config)
    
    # 5. 运行主程序
    connector = EmailConnector(config)
    exit_code = connector.run(args)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()