"""
日志系统使用示例

展示如何使用logger模块进行日志记录、性能监控等功能。
"""

import time
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import (
    setup_logging,
    get_logger,
    log_performance,
    log_function_call,
    LogContext,
    info,
    debug,
    warning,
    error
)
from src.utils.config_manager import ConfigManager


def example_basic_logging():
    """示例1: 基本日志记录"""
    print("\n" + "="*60)
    print("示例1: 基本日志记录")
    print("="*60)
    
    # 初始化配置管理器
    config = ConfigManager()
    
    # 初始化日志系统
    setup_logging(config)
    
    # 获取logger
    logger = get_logger(__name__)
    
    # 记录不同级别的日志
    logger.debug("这是一条调试信息")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
    logger.critical("这是一条严重错误信息")
    
    print("\n✓ 基本日志记录完成")


def example_module_loggers():
    """示例2: 不同模块的logger"""
    print("\n" + "="*60)
    print("示例2: 不同模块的logger")
    print("="*60)
    
    # 为不同模块创建logger
    imap_logger = get_logger('core.imap_client')
    parser_logger = get_logger('core.email_parser')
    csv_logger = get_logger('core.csv_writer')
    
    # 各模块记录日志
    imap_logger.info("IMAP客户端已连接到服务器")
    parser_logger.info("开始解析邮件")
    csv_logger.info("CSV文件写入成功")
    
    print("\n✓ 模块日志记录完成")


@log_performance
def slow_function():
    """一个耗时的函数"""
    time.sleep(1.5)
    return "完成"


def example_performance_monitoring():
    """示例3: 性能监控"""
    print("\n" + "="*60)
    print("示例3: 性能监控")
    print("="*60)
    
    # 使用性能监控装饰器
    result = slow_function()
    print(f"函数返回值: {result}")
    
    print("\n✓ 性能监控完成(查看日志查看耗时)")


@log_function_call
def process_email(email_id: str, save_attachment: bool = True):
    """处理邮件的示例函数"""
    return f"已处理邮件 {email_id}"


def example_function_call_logging():
    """示例4: 函数调用日志"""
    print("\n" + "="*60)
    print("示例4: 函数调用日志(需要DEBUG级别)")
    print("="*60)
    
    # 注意: 需要将日志级别设置为DEBUG才能看到函数调用日志
    logger = get_logger(__name__)
    
    with LogContext(logger, level=10):  # DEBUG = 10
        result = process_email("12345", save_attachment=True)
        print(f"函数返回值: {result}")
    
    print("\n✓ 函数调用日志完成")


def example_log_context():
    """示例5: 日志上下文"""
    print("\n" + "="*60)
    print("示例5: 日志上下文管理")
    print("="*60)
    
    logger = get_logger(__name__)
    
    logger.info("正常日志级别")
    
    # 临时使用DEBUG级别
    with LogContext(logger, level=10):
        logger.debug("临时DEBUG级别日志 - 只在此代码块中可见")
    
    logger.debug("这条DEBUG日志不会显示(除非全局级别是DEBUG)")
    logger.info("恢复正常日志级别")
    
    print("\n✓ 日志上下文管理完成")


def example_convenience_functions():
    """示例6: 便利函数"""
    print("\n" + "="*60)
    print("示例6: 便利函数(直接使用根logger)")
    print("="*60)
    
    # 使用便利函数(不需要获取logger实例)
    info("使用便利函数记录INFO日志")
    warning("使用便利函数记录WARNING日志")
    error("使用便利函数记录ERROR日志")
    
    print("\n✓ 便利函数使用完成")


def example_error_logging():
    """示例7: 异常日志记录"""
    print("\n" + "="*60)
    print("示例7: 异常日志记录")
    print("="*60)
    
    logger = get_logger(__name__)
    
    try:
        # 模拟一个错误
        result = 10 / 0
    except ZeroDivisionError as e:
        # 记录异常信息
        logger.error(f"发生除零错误: {e}", exc_info=True)
        print("\n✓ 异常已记录到日志")


def example_structured_logging():
    """示例8: 结构化日志"""
    print("\n" + "="*60)
    print("示例8: 结构化日志信息")
    print("="*60)
    
    logger = get_logger(__name__)
    
    # 记录结构化信息
    email_stats = {
        'total': 150,
        'processed': 145,
        'failed': 5,
        'duration': '2.5s'
    }
    
    logger.info(f"邮件处理统计: {email_stats}")
    
    # 使用extra参数(如果配置了支持)
    logger.info(
        "邮件处理完成",
        extra={
            'total': 150,
            'processed': 145,
            'failed': 5
        }
    )
    
    print("\n✓ 结构化日志记录完成")


def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("日志系统使用示例")
    print("="*60)
    
    try:
        # 运行各个示例
        example_basic_logging()
        example_module_loggers()
        example_performance_monitoring()
        example_function_call_logging()
        example_log_context()
        example_convenience_functions()
        example_error_logging()
        example_structured_logging()
        
        print("\n" + "="*60)
        print("所有示例运行完成!")
        print("="*60)
        print("\n提示:")
        print("- 控制台日志: 已显示在上方")
        print("- 文件日志: 请查看 logs/app.log")
        print("- 修改日志级别: 编辑 .env 文件中的 LOG_LEVEL")
        print("- 可选彩色日志: pip install colorlog")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()