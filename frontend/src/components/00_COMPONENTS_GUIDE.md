# Component 구조 메모

프론트엔드 UI 컴포넌트 설계 의도 및 역할 정리.

## UI Components (`src/components/ui`)
비즈니스 로직 없이, 오직 '보여주는' 역할만 함. (Dumb Component)

### BaseButton
- 공통 버튼.
- Props: `variant` (스타일), `size`, `loading`.
- 로딩 상태일 때 스피너 보여주고 클릭 막는 처리 되어 있음.

### CodeEditor
- 코드 입력 에디터. (Codemirror 등 라이브러리 랩핑)
- `v-model` 연동되도록 구현함. 외부에서는 내부 라이브러리 몰라도 됨.

### ResultViewer
- 테스트 실행 결과 표시용.
- 성공/실패 여부에 따라 테두리 색상이나 아이콘 달라짐. (`v-if` 분기 처리)

---

## Layout Components
앱의 틀을 잡는 녀석들.

### TheHeader
- 상단 네비게이션. 로고, 테마 토글, 깃허브 아이콘.
- 페이지 바뀌어도 고정됨 (`App.vue`에 있음).

### TheSidebar (HistoryDrawer)
- 과거 이력 리스트 + 설정 메뉴.
- 데스크탑: 왼쪽 고정 사이드바.
- 모바일: 버튼 누르면 나오는 Drawer 형태.
- **특이사항**: 모바일 Drawer는 `Teleport` 써서 `body` 태그 직하위로 렌더링함. (제일 위에 띄우려고)

---

## Data Flow (데이터 흐름 규칙)
1. **내려주기 (Props)**: 부모 -> 자식 데이터 전달.
2. **올려주기 (Emits)**: 자식 -> 부모 이벤트 전달 (클릭 등).
단방향 데이터 흐름 원칙 지킬 것.
