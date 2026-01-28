# LLM-based Automated Unit Test Generator (TESTER)

## 1. Overview
This project is a multi-language automated unit test generation system designed to enhance development productivity and ensure code quality. It leverages LLM capabilities (Gemini 2.0/3.0) while implementing a specialized architecture to minimize hallucinations and ensure syntactic correctness.

The system focuses on the dual-path validation of generated code through structural analysis and a self-correction feedback loop, making it a robust tool for QA engineering workflows.

## 2. Technical Stack
- **Frontend:** Vue.js 3, Vite, Tailwind CSS v4, Lucide Icons, Highlight.js
- **Backend:** Python 3.12, FastAPI (Asynchronous SSE Streaming), Pydantic (Data Validation)
- **AI/LLM:** Google Gemini API (Flash/Pro)
- **Testing & Verification:** Pytest, Custom Chaos Testing Suite
- **Infrastructure:** Docker (Multi-stage build), Google Cloud Run

## 3. System Architecture
The system is built on a modular architecture that separates linguistic concerns from the core generation logic.

### Design Pattern: Strategy Pattern
To support multiple programming languages (Python, Java, JavaScript) without tight coupling, the `LanguageStrategy` interface was implemented.
- **Linguistic Encapsulation:** Each language defines its own syntax validation, system instructions, and error correction prompts.
- **Factory Pattern:** `LanguageFactory` dynamically resolves the appropriate strategy at runtime based on user input.

### Data Flow & 2-Pass Reflection
1. **Client Request:** Vue.js client sends source code and configuration via POST.
2. **Preprocessing:** FastAPI validates input using the selected `LanguageStrategy`.
3. **Draft Generation (Pass 1):** `GeminiService` generates an initial set of test cases.
4. **Self-Reflection (Pass 2):** The `_reflect_and_refine` logic re-injects the draft into the LLM with a "Strict Syntax Nazi" persona to verify linguistic consistency and imports.
5. **Streaming Response:** The refined code is streamed back to the client using Server-Sent Events (SSE).

## 4. Key Features & Implementation
- **Cross-Language Validation:** Implements regex-based guardrails to prevent linguistic bleeding (e.g., ensuring Java imports are present in Java outputs).
- **Syntactic Guardrails:** Validates executable code segments before rendering, reducing the risk of "broken" code delivery.
- **Asynchronous Processing:** Utilizes Python's `asyncio` and `StreamingResponse` to provide a real-time feedback experience.

## 5. Robustness & QA Verification
### Chaos Testing Suite
A specialized testing framework (`tests/chaos_runner.py`) was implemented to verify system resilience against malicious or malformed inputs:
- **The Chimera Case:** Mixed-language inputs to test linguistic identification.
- **The Fragment Case:** Contextless code snippets to verify inference capabilities.
- **The Trap Case:** Content-free (comments only) code to prevent hallucination.
- **The Injection Case:** Guardrail verification against prompt injection attempts.

### Automated Evaluation
The `backend/tests/` directory contains automated evaluation scripts (`auto_evaluator.py`) designed for integration into CI/CD pipelines to measure generation success rates.

## 6. Project Structure
```text
.
├── backend/                # FastAPI backend service
│   ├── src/
│   │   ├── languages/      # Strategy pattern implementation
│   │   ├── services/       # Core LLM integration (Reflection logic)
│   │   └── main.py         # API entry point
│   └── tests/              # Unit & Integration tests
├── frontend/               # Vue.js 3 SPA
│   ├── src/
│   │   ├── App.vue         # Main interactive UI
│   │   └── style.css       # Tailwind v4 configuration
│   └── vite.config.ts      # Build configuration
├── tests/                  # System-wide Robustness (Chaos) tests
├── Dockerfile              # Multi-stage container definition
└── README.md
```

## 7. Setup & Execution
### Prerequisites
- Python 3.12+, Node.js 20+
- Google Gemini API Key

### Local Development (Backend)
```bash
cd backend
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
python src/main.py
```

### Local Development (Frontend)
```bash
cd frontend
npm install
npm run dev
```

### Chaos Test Execution
```bash
python tests/chaos_runner.py
```
