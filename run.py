import sys
import os
from streamlit.web import cli as stcli
from streamlit.runtime import Runtime

def main():
    """애플리케이션 진입점"""
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    if Runtime.exists():
        import src.app as app
        app.main()
    else:
        sys.argv = ["streamlit", "run", "src/app.py"]
        sys.exit(stcli.main())

if __name__ == "__main__":
    main()
