"""
파일 목적 : 프로젝트 전역에서 공통으로 사용하는 로거(Logger) 생성 유틸리티

작성자 : 박지우 / 작성일 : 2026-02-04
작성자 : - / 수정일 : -

설정 목적 :
- 모듈별로 독립된 로거를 생성하여 파일 및 콘솔에 동시에 출력한다.
- logs 디렉토리 아래에 날짜별로 로그 파일을 자동 생성한다.
- TimedRotatingFileHandler를 사용하여 자정마다 로그 파일을 회전(rotate)하고,
  최대 14일치 로그를 보관한다.

기타 주의 사항 :
- logger.handlers.clear()로 중복 핸들러 등록을 방지한다.
- 프로젝트 루트 기준으로 logs 폴더가 자동 생성된다.
"""

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