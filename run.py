import sys
from streamlit.web import cli as stcli

def main():
    """
    Streamlit 애플리케이션의 진입점입니다.
    src/app.py를 실행합니다.
    """
    sys.argv = ["streamlit", "run", "src/app.py"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
