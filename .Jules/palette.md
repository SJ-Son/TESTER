## 2025-02-18 - Language Selection Accessibility
**Learning:** Icon-only or abbreviated buttons (like "PY", "JS") require descriptive ARIA labels. Adding a `name` property to data objects (e.g., `{ label: 'PY', name: 'Python' }`) is a clean pattern to support both concise UI and accessible descriptions without complex template logic.
**Action:** Apply this `label`/`name` data structure pattern when adding other abbreviated selection controls.
