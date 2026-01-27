import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    지정된 이름의 로거를 반환합니다.
    포맷: [시간] [로그레벨] 메시지 (모두 한글 친화적 설정은 아님, 표준 포맷 준수)
    """
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 설정되어 있다면 중복 추가 방지
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 콘솔 핸들러 (StreamHandler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger
