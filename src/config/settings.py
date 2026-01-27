import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    애플리케이션 설정을 관리하는 클래스입니다.
    배포 환경(Streamlit Cloud)의 1순위: st.secrets
    로컬 환경(Local)의 2순위: os.getenv(.env)
    """

    @property
    def GEMINI_API_KEY(self) -> str:
        """
        Gemini API 키를 반환합니다.
        Streamlit Secrets를 우선 확인하고, 없으면 환경 변수를 확인합니다.
        """
        # 1. Streamlit Secrets 확인 (Cloud)
        try:
            if "GEMINI_API_KEY" in st.secrets:
                return st.secrets["GEMINI_API_KEY"]
        except (FileNotFoundError, AttributeError):
            pass  # 로컬 환경에서 secrets.toml이 없을 수 있음

        # 2. Environment Variable 확인 (Local .env)
        return os.getenv("GEMINI_API_KEY", "")

    def validate(self):
        """필수 설정값이 존재하는지 검증합니다."""
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY가 설정되지 않았습니다. "
                ".env 파일 또는 Streamlit Secrets를 확인해주세요."
            )

# 싱글톤 인스턴스
settings = Settings()
