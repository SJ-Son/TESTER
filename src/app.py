"""
QA 테스트 코드 생성기 UI.
"""
import time
import streamlit as st

from src.languages.factory import LanguageFactory
from src.services.gemini_service import GeminiService
from src.utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(
    page_title="QA Test Code Generator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_service(model_name: str) -> GeminiService:
    return GeminiService(model_name=model_name)



def check_rate_limit() -> tuple[bool, str]:
    cooldown = 5
    last_req = st.session_state.get('last_request_time', 0)
    
    elapsed = time.time() - last_req
    if elapsed < cooldown:
        return False, f"⏳ {int(cooldown - elapsed)}초 후 다시 시도하세요."
    
    st.session_state['last_request_time'] = time.time()
    return True, ""

def main():
    st.title("Test Code Generator")
    
    # Sidebar
    st.sidebar.header("Settings")
    
    # Language Selector
    language = st.sidebar.selectbox(
        "Language",
        LanguageFactory.get_supported_languages()
    )
    strategy = LanguageFactory.get_strategy(language)
    
    model_name = st.sidebar.selectbox(
        "Model",
        ["gemini-3-flash-preview", "gemini-3-pro-preview"]
    )
    st.sidebar.divider()
    st.sidebar.info("Tip: 동일 코드는 캐싱됩니다.")
    
    try:
        service = get_service(model_name)
    except Exception as e:
        st.error("서비스 초기화 실패")
        logger.error(f"Init Error: {e}")
        return

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input")
        code_input = st.text_area(
            f"{language} Code",
            height=400,
            placeholder=strategy.get_placeholder(),
            key="user_input",
            label_visibility="collapsed"
        )
        btn_gen = st.button("Generate Test Code", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("Output")
        
        if btn_gen:
            valid, msg = strategy.validate_code(code_input)
            if not valid:
                st.warning(msg)
                return

            ok, limit_msg = check_rate_limit()
            if not ok:
                st.warning(limit_msg)
                return
            
            with st.spinner(f"Generating {language} Test Code..."):
                try:
                    start = time.time()
                    
                    # Streaming 처리
                    response_placeholder = st.empty()
                    full_response = ""
                    
                    # GeminiService는 이제 Generator를 반환 (stream=True 기본)
                    stream_generator = service.generate_test_code(
                        code_input, 
                        system_instruction=strategy.get_system_instruction(),
                        stream=True
                    )
                    
                    for chunk in stream_generator:
                        full_response += chunk
                        # 실시간 렌더링 (Markdown Code Block 유지)
                        # 전략에서 UI 언어 코드 가져오기
                        ui_lang = strategy.get_streamlit_language()
                        response_placeholder.markdown(f"```{ui_lang}\n{full_response}\n```")
                        
                    elapsed = time.time() - start
                    st.success(f"Done! ({elapsed:.2f}s)")
                    
                except Exception as e:
                    st.error("처리 중 오류가 발생했습니다.")
                    logger.error(f"Generate Error: {e}")
        else:
            st.info("좌측에 코드를 입력하고 실행하세요.")

if __name__ == "__main__":
    main()
