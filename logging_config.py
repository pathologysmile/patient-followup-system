"""
日志配置模块
提供统一的日志记录功能，便于问题排查和系统维护
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    配置日志系统
    
    功能：
    - 按日期创建日志文件
    - 支持日志轮转（避免文件过大）
    - 同时输出到文件和控制台
    - 分级记录（DEBUG/INFO/WARNING/ERROR/CRITICAL）
    
    返回:
        logger: 配置好的日志记录器
    """
    # 创建日志目录
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # 日志文件名（按日期）
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    # 创建logger
    logger = logging.getLogger('PatientReminderSystem')
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（带轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=10,          # 保留10个备份
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # 控制台只显示WARNING及以上
    console_handler.setFormatter(formatter)
    
    # 错误日志单独文件
    error_log_file = os.path.join(log_dir, f'error_{datetime.now().strftime("%Y%m%d")}.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # 添加handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)
    
    return logger


# 创建全局logger实例
logger = setup_logging()


def log_user_action(action, user_info='', details=''):
    """
    记录用户操作日志
    
    参数:
        action: 操作类型（如：登录、保存、删除等）
        user_info: 用户信息（可选）
        details: 详细信息（可选）
    """
    logger.info(f"用户操作 | {action} | {user_info} | {details}")


def log_system_event(event_type, message, level='INFO'):
    """
    记录系统事件日志
    
    参数:
        event_type: 事件类型（如：启动、停止、备份等）
        message: 事件描述
        level: 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL）
    """
    log_message = f"系统事件 | {event_type} | {message}"
    
    if level == 'DEBUG':
        logger.debug(log_message)
    elif level == 'INFO':
        logger.info(log_message)
    elif level == 'WARNING':
        logger.warning(log_message)
    elif level == 'ERROR':
        logger.error(log_message)
    elif level == 'CRITICAL':
        logger.critical(log_message)


def log_database_operation(operation, table_name, success=True, error_msg=''):
    """
    记录数据库操作日志
    
    参数:
        operation: 操作类型（INSERT/UPDATE/DELETE/SELECT）
        table_name: 表名
        success: 是否成功
        error_msg: 错误信息（如果失败）
    """
    status = "成功" if success else "失败"
    message = f"数据库操作 | {operation} | {table_name} | {status}"
    
    if success:
        logger.info(message)
    else:
        logger.error(f"{message} | 错误: {error_msg}")


def log_api_call(api_name, params='', response_time=0, success=True):
    """
    记录API调用日志
    
    参数:
        api_name: API名称
        params: 请求参数（脱敏后）
        response_time: 响应时间（毫秒）
        success: 是否成功
    """
    status = "成功" if success else "失败"
    message = f"API调用 | {api_name} | 耗时: {response_time}ms | {status}"
    
    if params:
        message += f" | 参数: {params}"
    
    if success:
        logger.info(message)
    else:
        logger.error(message)


def get_log_stats():
    """
    获取日志统计信息
    
    返回:
        dict: 包含日志文件信息的字典
    """
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        return {'total_files': 0, 'total_size': 0, 'files': []}
    
    files = []
    total_size = 0
    
    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath)
            total_size += size
            files.append({
                'name': filename,
                'size': size,
                'size_mb': round(size / (1024 * 1024), 2),
                'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return {
        'total_files': len(files),
        'total_size': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'files': sorted(files, key=lambda x: x['modified'], reverse=True)
    }
