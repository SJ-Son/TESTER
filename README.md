# 🧪 QA Test Code Generator

**파이썬 코드를 입력하면 AI가 자동으로 완벽한 테스트 코드를 생성해주는 프로덕션 레벨 Streamlit 애플리케이션입니다.**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.41-red.svg)](https://streamlit.io)
[![Gemini API](https://img.shields.io/badge/gemini-3.0-purple.svg)](https://ai.google.dev/)

---

## ✨ 주요 기능

### 1. 🛡️ 보안 강화
- **프롬프트 인젝션 방어**: 악의적인 시스템 지시 무시 시도 차단
- **AST 검증**: 유효한 파이썬 코드만 API로 전송 (비용 절감)
- **Secrets 우선순위**: `st.secrets` → `.env` 순서로 안전한 키 관리

### 2. 🎨 사용자 경험(UX)
- **2단 레이아웃**: 입력/출력 분리로 직관적인 인터페이스
- **상태 유지**: 사이드바 조작 시에도 입력 코드 보존
- **친화적 피드백**: 명확한 성공/경고/에러 메시지

### 3. ⚡ 성능 최적화
- **캐싱**: 동일 코드 재요청 시 즉시 반환 (TTL 1시간)
- **Rate Limiting**: 5초 쿨타임으로 API 비용 절감
- **모델 선택**: Gemini 3.0 Flash/Pro 지원

### 4. ✅ 품질 보증
- **100% Mocking 테스트**: pytest-mock으로 무료 테스트
- **재시도 로직**: 최대 3회 자동 재시도 (tenacity)

---

## 📁 프로젝트 구조

```
qa-test-generator/
├── run.py                      # 실행 진입점
├── requirements.txt            # 의존성
├── .env                        # API 키 (로컬용, Git 제외)
├── .gitignore                  # 보안 설정
├── README.md                   # 프로젝트 문서
│
├── src/
│   ├── app.py                  # 메인 UI (Streamlit)
│   ├── config/
│   │   └── settings.py         # 환경 변수 관리
│   ├── services/
│   │   └── gemini_service.py   # Gemini API 로직
│   └── utils/
│       ├── logger.py           # 로깅 설정
│       └── prompts.py          # 시스템 프롬프트
│
└── tests/
    └── test_gemini.py          # 단위 테스트
```

---

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 Gemini API 키를 입력하세요:
```bash
GEMINI_API_KEY=your_api_key_here
```

> **배포 환경 (Streamlit Cloud)**: 
> Dashboard → Settings → Secrets에서 `GEMINI_API_KEY` 추가

### 3. 애플리케이션 실행
```bash
# 방법 1: run.py 사용 (권장)
python run.py

# 방법 2: 직접 실행
streamlit run src/app.py
```

### 4. 테스트 실행
```bash
pytest tests/test_gemini.py -v
```

---

## 🔧 기술 스택

| 카테고리 | 기술 |
|---------|------|
| **프레임워크** | Streamlit 1.41 |
| **AI 모델** | Google Gemini 3.0 (Flash/Pro) |
| **환경 관리** | python-dotenv |
| **테스트** | pytest, pytest-mock |
| **재시도** | tenacity |

---

## 💡 사용 예시

### 입력 예시
```python
def add(a, b):
    return a + b
```

### 출력 예시
```python
import pytest

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(0, 5) == 5
```

---

## 🛡️ 보안 검증 기능

### 1. AST 검증
```python
# ❌ 차단: 유효하지 않은 코드
"안녕하세요" → st.warning("유효한 파이썬 코드가 아닙니다")

# ✅ 허용: 유효한 파이썬 코드
def foo(): pass → API 호출
```

### 2. 길이 제한
```python
# ❌ 차단: 3000자 초과
len(code) > 3000 → st.error("입력 코드가 너무 깁니다")
```

### 3. Rate Limiting
```python
# ❌ 차단: 5초 이내 재요청
elapsed < 5 → st.warning("⏳ {remaining}초 후에 다시 시도해주세요")
```

---

## 📊 캐싱 전략

### 서비스 인스턴스 캐싱
```python
@st.cache_resource
def get_gemini_service(model_name: str) -> GeminiService:
    # 모델 변경 시에만 재생성
    return GeminiService(model_name=model_name)
```

### API 응답 캐싱
```python
@st.cache_data(show_spinner=False, ttl=3600)
def generate_code_test(_service, code: str) -> str:
    # 1시간 동안 캐싱 (동일 코드 재요청 시 즉시 반환)
    return _service.generate_test_code(code)
```

---

## 🧪 테스트

### 테스트 커버리지
- ✅ 서비스 초기화 테스트
- ✅ 정상 코드 생성 테스트 (Mocking)
- ✅ 빈 입력 처리 테스트
- ✅ API 에러 재시도 테스트
- ✅ 빈 응답 처리 테스트

### 실행 결과
```bash
============================= test session starts ==============================
collected 5 items

tests/test_gemini.py::test_service_initialization PASSED           [ 20%]
tests/test_gemini.py::test_generate_test_code_success PASSED       [ 40%]
tests/test_gemini.py::test_generate_test_code_empty_input PASSED   [ 60%]
tests/test_gemini.py::test_generate_test_code_api_error PASSED     [ 80%]
tests/test_gemini.py::test_generate_test_code_empty_response PASSED [100%]

========================= 5 passed in 4.48s =========================
```

---

## 🔑 환경 변수

| 변수명 | 설명 | 필수 |
|-------|------|-----|
| `GEMINI_API_KEY` | Google Gemini API 키 | ✅ |

### 로컬 환경
`.env` 파일에 저장:
```bash
GEMINI_API_KEY=your_api_key_here
```

### 배포 환경 (Streamlit Cloud)
Dashboard → Settings → Secrets:
```toml
GEMINI_API_KEY = "your_api_key_here"
```

---

## 📝 Git 워크플로우

이 프로젝트는 엄격한 브랜치 전략을 사용합니다:

```bash
# 1. 기능 브랜치 생성
git checkout -b feat/feature-name

# 2. 작업 후 커밋
git add .
git commit -m "기능추가: 기능 설명"

# 3. main 브랜치로 병합
git checkout main
git merge feat/feature-name

# 4. 브랜치 정리
git branch -d feat/feature-name
```

---

## 🤝 기여 가이드

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m '기능추가: 놀라운 기능'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

---

## 📄 라이선스

이 프로젝트는 개인 학습 목적으로 제작되었습니다.

---

## 🙏 감사의 말

- **Google Gemini**: 강력한 AI 모델 제공
- **Streamlit**: 빠른 프로토타입과 배포
- **pytest**: 안정적인 테스트 프레임워크

---

## 📞 문의

질문이나 제안사항이 있으시면 이슈를 등록해주세요!

**Made with ❤️ by SJ-Son**
