import streamlit as st
import time
import ast
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
        options=["gemini-3-flash-preview", "gemini-3-pro-preview"],
        index=0,
        help="Flash: 빠르고 효율적 (v3.0), Pro: 고성능 추론 (v3.0)"
    )
    st.sidebar.markdown("---")
    st.sidebar.info("💡 동일한 코드는 캐싱된 결과를 빠르게 반환합니다.")

    # 서비스 초기화
    try:
        service = get_gemini_service(model_name)
    except Exception as e:
        st.error("AI 서비스를 초기화하는 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.")
        logger.error(f"서비스 초기화 오류: {e}")
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
            # 1. 입력 검증 (Empty check)
            if not code_input.strip():
                st.warning("코드를 입력해주세요.")
                return

            # 2. 입력 검증 (Length check)
            if len(code_input) > 3000:
                st.error("입력 코드가 너무 깁니다. (3000자 제한)")
                return

            # 3. 입력 검증 (AST Parsing)
            try:
                ast.parse(code_input)
            except SyntaxError:
                st.warning("유효한 파이썬 코드가 아닙니다. 문법을 확인해주세요.")
                return

            # 4. 속도 제한 (Rate Limiting)
            if 'last_req_time' not in st.session_state:
                st.session_state['last_req_time'] = 0
            
            current_time = time.time()
            if current_time - st.session_state['last_req_time'] < 5:
                st.warning("요청이 너무 빠릅니다. 잠시 후 다시 시도해주세요.")
                return
            
            st.session_state['last_req_time'] = current_time

            with st.spinner("테스트 코드 작성 중..."):
                try:
                    start_time = time.time()
                    result = generate_code_test(service, code_input)
                    elapsed = time.time() - start_time
                    
                    st.success(f"생성 완료 ({elapsed:.2f}s)")
                    st.code(result, language="python")
                except Exception as e:
                    st.error("AI 서버가 혼잡합니다. 잠시 후 다시 시도해주세요.")
                    logger.error(f"생성 실패: {e}")
        else:
            st.info("코드를 입력하고 버튼을 눌러주세요.")

if __name__ == "__main__":
    main()
