import sys
import os
from streamlit.web import cli as stcli

def main():
    """
    애플리케이션 진입점 (Entry Point).
    Streamlit CLI를 통해 애플리케이션을 실행합니다.
    """
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    # Streamlit 실행 명령 구성
    sys.argv = ["streamlit", "run", "src/app.py"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
