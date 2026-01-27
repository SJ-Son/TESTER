import sys
import os
from streamlit.web import cli as stcli
from streamlit.runtime import Runtime

def main():
    """
    애플리케이션 진입점 (Entry Point).
    
    1. `python run.py`로 실행 시: Streamlit CLI를 통해 애플리케이션을 실행합니다.
    2. `streamlit run run.py`로 실행 시: 이미 Runtime이 존재하므로 src/app.py를 직접 실행합니다.
    """
    # src 디렉토리를 경로에 추가하여 모듈 import가 가능하게 함
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    if Runtime.exists():
        # 이미 Streamlit Runtime 내에서 실행 중인 경우 (예: Streamlit Cloud)
        import src.app as app
        app.main()
    else:
        # 일반 Python 스크립트로 실행된 경우
        sys.argv = ["streamlit", "run", "src/app.py"]
        sys.exit(stcli.main())

if __name__ == "__main__":
    main()
