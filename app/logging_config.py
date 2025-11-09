# app/logging_config.py

import logging
import sys
from loguru import logger
from pathlib import Path  # <-- 1. 导入 pathlib

# --- 2. 定义绝对路径 ---
# (Path(__file__) 是 '.../my_project/app/logging_config.py')
# .parent 是 '.../my_project/app'
# .parent.parent 是 '.../my_project' (我们的项目根目录)
BASE_DIR = Path(__file__).parent.parent

# 我们的日志目录和文件的绝对路径
LOG_DIR = BASE_DIR / "logs"
LOG_FILE_PATH = LOG_DIR / "my_project.log"

# --- 3. (新!) 自动创建日志目录 ---
# (如果 'logs' 目录不存在，就创建它)
LOG_DIR.mkdir(parents=True, exist_ok=True)


# 1. 定义 Loguru 的日志格式 (保持不变)
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# 2. 移除 Loguru 的默认 handler
logger.remove()

# 3. 添加终端 handler (保持不变)
logger.add(
    sys.stderr,
    level="DEBUG",
    format=log_format,
    colorize=True,
)

# 4. 添加文件 handler (使用我们的新路径)
logger.add(
    LOG_FILE_PATH,  # <-- 4. 使用绝对路径
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    format=log_format,
    encoding="utf-8",
)

# 5. 拦截处理器 (保持不变)
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

# 6. setup 函数 (保持不变)
def setup_logging():
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    logger.info("日志系统设置完毕 (绝对路径已启用)。已开始拦截标准日志...")