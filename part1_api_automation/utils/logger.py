import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

def get_logger(module_file=__file__, level=logging.INFO):
    """
    - 프로젝트 루트 기준 logs 폴더 생성
    - 모듈별 파일명
    - 날짜별 회전
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(module_file))))
    
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    module_name = os.path.splitext(os.path.basename(module_file))[0]
    
    date_prefix = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{module_name}_{date_prefix}.log")
    
    logger = logging.getLogger(module_name)
    logger.setLevel(level)
    logger.propagate = False
    logger.handlers.clear()
    
    if not logger.handlers:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        file_handler = TimedRotatingFileHandler(
            log_file, when="midnight", interval=1, backupCount=14, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

logger = get_logger()