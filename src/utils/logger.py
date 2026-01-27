import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    애플리케이션 전역에서 사용할 로거를 설정하고 반환합니다.
    
    기본적으로 INFO 레벨 이상의 로그를 콘솔(표준 출력)에 출력하도록 설정됩니다.
    로그 포맷은 '[시간] [레벨] [모듈명]: 메시지' 형태입니다.

    Args:
        name (str): 로거를 요청한 모듈의 이름 (보통 __name__을 전달)

    Returns:
        logging.Logger: 설정이 완료된 로거 인스턴스
    """
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 설정되어 있다면 중복 추가 방지를 위해 기존 로거 반환
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)

    # 콘솔 핸들러 설정
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # 로그 포맷 정의
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
