import streamlit as st
import time
from src.services.gemini_service import GeminiService
from src.utils.logger import get_logger

# 로거 설정
logger = get_logger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="Code Tester AI",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 캐싱: 서비스 인스턴스 생성 (리소스 연결)
@st.cache_resource
def get_gemini_service(model_name: str) -> GeminiService:
    """
    GeminiService 인스턴스를 생성하고 캐싱합니다.
    모델명이 변경되면 새로운 인스턴스를 생성합니다.
    """
    logger.info(f"GeminiService 인스턴스 생성: {model_name}")
    return GeminiService(model_name=model_name)

# 캐싱: 결과 생성 (데이터)
@st.cache_data(show_spinner=False)
def generate_code_test(_service: GeminiService, code: str) -> str:
    """
    GeminiService를 통해 테스트 코드를 생성하고 결과를 캐싱합니다.
    _service 인자는 해싱에서 제외하기 위해 언더바(_)를 붙입니다.
    """
    return _service.generate_test_code(code)

def main():
    st.title("🧪 Code Tester AI")
    st.markdown("### 파이썬 코드를 입력하면 완벽한 테스트 코드를 작성해드립니다.")

    # [사이드바] 모델 선택
    st.sidebar.header("설정 (Configuration)")
    model_name = st.sidebar.selectbox(
        "사용할 모델 선택",
        options=["gemini-1.5-flash", "gemini-1.5-pro"],
        index=0,
        help="Flash는 빠르고 경제적이며, Pro는 더 복잡한 추론에 강합니다."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip:** 동일한 코드에 대한 요청은 캐싱되어 빠르게 결과를 불러옵니다.")

    # 서비스 초기화
    try:
        service = get_gemini_service(model_name)
    except Exception as e:
        st.error(f"서비스 초기화 중 오류가 발생했습니다: {e}")
        return

    # [메인 레이아웃] 화면 분할 (Split View)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📝 Input Code")
        code_input = st.text_area(
            "테스트하고 싶은 파이썬 코드를 입력하세요:",
            height=400,
            placeholder="def add(a, b):\n    return a + b",
            help="여기에 파이썬 코드를 붙여넣으세요."
        )
        
        generate_btn = st.button("🚀 테스트 코드 생성하기", use_container_width=True)

    with col2:
        st.subheader("💻 Test Code Result")
        
        if generate_btn and code_input:
            with st.spinner("AI가 코드를 분석하고 테스트를 작성 중입니다..."):
                try:
                    start_time = time.time()
                    
                    # API 호출 (캐싱 적용됨)
                    result = generate_code_test(service, code_input)
                    
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    
                    st.success(f"생성 완료! ({elapsed_time:.2f}초 소요)")
                    st.code(result, language="python")
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
                    logger.error(f"UI 생성 오류: {e}")
        elif generate_btn and not code_input:
            st.warning("코드를 입력해야 합니다.")
        else:
            st.info("왼쪽에 코드를 입력하고 버튼을 눌러주세요.")

if __name__ == "__main__":
    main()
