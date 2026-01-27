import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """애플리케이션 환경 변수 관리."""
    
    # Streamlit Secrets 우선 확인, 없으면 환경변수 사용
    # 로컬 테스트 환경 등 secrets가 없는 경우를 대비해 try-except 처리
    try:
        _secrets_key = st.secrets.get("GEMINI_API_KEY")
    except (FileNotFoundError, Exception): 
        # StreamlitSecretNotFoundError 등 발생 시
        _secrets_key = None
        
    GEMINI_API_KEY: str = _secrets_key or os.getenv("GEMINI_API_KEY", "")

    @staticmethod
    def validate():
        """필수 환경 변수 검증."""
        if not Settings.GEMINI_API_KEY:
             raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
