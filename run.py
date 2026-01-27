import sys
import os

# 프로젝트 루트를 sys.path에 추가하여 모듈 임포트가 원활하게 작동하도록 함
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import main

if __name__ == "__main__":
    main()
