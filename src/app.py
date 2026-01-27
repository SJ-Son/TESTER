"""
QA 테스트 코드 생성기 메인 UI입니다.
보안, UX, 성능 최적화가 적용된 프로덕션 레벨 구현입니다.
"""
import streamlit as st
import time
import ast

from src.services.gemini_service import GeminiService
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="🧪 QA Test Code Generator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def get_gemini_service(model_name: str) -> GeminiService:
    """
    GeminiService 인스턴스를 생성하고 캐싱합니다.
    모델명이 변경될 때만 새로 생성됩니다.
    """
    logger.info(f"서비스 인스턴스 생성: {model_name}")
    return GeminiService(model_name=model_name)


@st.cache_data(show_spinner=False, ttl=3600)
def generate_code_test(_service: GeminiService, code: str) -> str:
    """
    테스트 코드를 생성하고 결과를 캐싱합니다.
    동일한 코드에 대한 재요청 시 API 호출 없이 즉시 반환됩니다.
    """
    return _service.generate_test_code(code)


def validate_python_code(code: str) -> tuple[bool, str]:
    """
    파이썬 코드의 유효성을 검증합니다.
    
    Returns:
        (유효여부, 에러메시지)
    """
    # 1. 빈 입력 체크
    if not code.strip():
        return False, "코드를 입력해주세요."
    
    # 2. 길이 체크
    if len(code) > 3000:
        return False, "입력 코드가 너무 깁니다. (최대 3000자)"
    
    # 3. AST 파싱으로 유효한 파이썬 코드인지 확인
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError:
        return False, "유효한 파이썬 코드가 아닙니다. 문법을 확인해주세요."


def check_rate_limit() -> tuple[bool, str]:
    """
    사용자의 요청 속도를 체크합니다.
    
    Returns:
        (허용여부, 메시지)
    """
    cooldown_seconds = 5
    
    if 'last_request_time' not in st.session_state:
        st.session_state['last_request_time'] = 0
    
    current_time = time.time()
    elapsed = current_time - st.session_state['last_request_time']
    
    if elapsed < cooldown_seconds:
        remaining = int(cooldown_seconds - elapsed)
        return False, f"⏳ {remaining}초 후에 다시 시도해주세요."
    
    st.session_state['last_request_time'] = current_time
    return True, ""


def main():
    """메인 애플리케이션 함수입니다."""
    
    # 타이틀
    st.title("🧪 QA Test Code Generator")
    st.markdown("### 파이썬 코드를 입력하면 완벽한 테스트 코드를 자동 생성합니다")
    
    # 사이드바: 모델 선택
    st.sidebar.header("⚙️ 설정")
    model_name = st.sidebar.selectbox(
        "AI 모델 선택",
        options=["gemini-3-flash-preview", "gemini-3-pro-preview"],
        index=0,
        help="Flash: 빠르고 효율적 / Pro: 고성능 추론"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip**: 동일한 코드는 캐싱되어 즉시 반환됩니다!")
    
    # 서비스 초기화
    try:
        service = get_gemini_service(model_name)
    except Exception as e:
        st.error("⚠️ AI 서비스를 초기화하는 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.")
        logger.error(f"서비스 초기화 실패: {e}")
        return
    
    # 2단 레이아웃
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Input Code")
        
        # 상태 유지를 위한 key 사용
        code_input = st.text_area(
            "파이썬 코드를 입력하세요:",
            height=400,
            placeholder="def add(a, b):\n    return a + b",
            help="테스트할 파이썬 코드를 입력하세요.",
            key="user_input"  # 핵심: 상태 유지
        )
        
        generate_btn = st.button(
            "🚀 테스트 코드 생성",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        st.subheader("💻 Generated Test Code")
        
        if generate_btn:
            # 1. 입력 검증
            is_valid, error_msg = validate_python_code(code_input)
            if not is_valid:
                st.warning(error_msg)
                return
            
            # 2. 속도 제한 체크
            can_proceed, rate_msg = check_rate_limit()
            if not can_proceed:
                st.warning(rate_msg)
                return
            
            # 3. 테스트 코드 생성
            with st.spinner("🤖 AI가 테스트 코드를 작성하고 있습니다..."):
                try:
                    start_time = time.time()
                    result = generate_code_test(service, code_input)
                    elapsed = time.time() - start_time
                    
                    st.success(f"✅ 생성 완료! ({elapsed:.2f}초)")
                    st.code(result, language="python", line_numbers=True)
                    
                except Exception as e:
                    st.error("⚠️ AI 서버가 혼잡합니다. 잠시 후 다시 시도해주세요.")
                    logger.error(f"테스트 코드 생성 실패: {e}")
        else:
            st.info("👈 왼쪽에 코드를 입력하고 버튼을 눌러주세요.")


if __name__ == "__main__":
    main()
