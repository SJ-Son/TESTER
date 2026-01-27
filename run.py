import sys
import os

# 현재 디렉토리를 sys.path에 추가 (모듈 로딩 문제 해결)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import main

if __name__ == "__main__":
    main()
