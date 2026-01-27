import streamlit as st
import time
from src.services.gemini_service import GeminiService
from src.utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(
    page_title="Code Tester AI",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_gemini_service(model_name: str) -> GeminiService:
    """GeminiService 인스턴스 생성 및 캐싱 (리소스 재사용)."""
    logger.info(f"서비스 인스턴스 생성: {model_name}")
    return GeminiService(model_name=model_name)

@st.cache_data(show_spinner=False)
def generate_code_test(_service: GeminiService, code: str) -> str:
    """테스트 코드 생성 결과 캐싱 (데이터 재사용)."""
    return _service.generate_test_code(code)

def main():
    st.title("🧪 Code Tester AI")
    st.markdown("### 파이썬 코드를 입력하면 완벽한 테스트 코드를 작성해드립니다.")

    # [사이드바] 설정
    st.sidebar.header("설정 (Configuration)")
    model_name = st.sidebar.selectbox(
        "사용할 모델 선택",
        options=["gemini-2.0-flash", "gemini-2.5-pro"],
        index=0,
        help="Flash: 빠름/경제적 (v2.0), Pro: 고성능 추론 (v2.5)"
    )
    st.sidebar.markdown("---")
    st.sidebar.info("💡 동일한 코드는 캐싱된 결과를 빠르게 반환합니다.")

    # 서비스 초기화
    try:
        service = get_gemini_service(model_name)
    except Exception as e:
        st.error(f"서비스 초기화 오류: {e}")
        return

    # [메인] Split View
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📝 Input Code")
        code_input = st.text_area(
            "파이썬 코드 입력:",
            height=400,
            placeholder="def add(a, b):\n    return a + b",
            help="여기에 소스 코드를 붙여넣으세요."
        )
        generate_btn = st.button("🚀 테스트 코드 생성", use_container_width=True)

    with col2:
        st.subheader("💻 Test Code Result")
        
        if generate_btn:
            if not code_input.strip():
                st.warning("코드를 입력해주세요.")
                return

            with st.spinner("테스트 코드 작성 중..."):
                try:
                    start_time = time.time()
                    result = generate_code_test(service, code_input)
                    elapsed = time.time() - start_time
                    
                    st.success(f"생성 완료 ({elapsed:.2f}s)")
                    st.code(result, language="python")
                except Exception as e:
                    st.error(f"오류 발생: {e}")
                    logger.error(f"생성 실패: {e}")
        else:
            st.info("코드를 입력하고 버튼을 눌러주세요.")

if __name__ == "__main__":
    main()
