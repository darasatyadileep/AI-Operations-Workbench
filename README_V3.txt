AI OPERATIONS WORKBENCH V3
==========================

What changed
------------
V3 redesigns all four modules around the same product pattern:
1. Explain the business problem.
2. Show an example-case process scheme.
3. Expose meaningful inputs.
4. Run the AI/optimization workflow.
5. Present decision-oriented outputs and interpretation.

Module 1 - Compressor Health
- Business-problem framing and process scheme.
- CSV upload and one-click built-in sample case.
- Health status, thresholds and anomaly trend visualization.

Module 2 - Feed Optimizer
- Feed -> Plant -> Fractionator -> Products schematic.
- Editable feed, capacity and price inputs.
- Excel upload support.
- Optimization objective/constraints explained.
- KPI and plant-loading results dashboard.

Module 3 - Visual Inspection
- Field image -> preprocessing -> OCR -> asset record scheme.
- Image upload/preview.
- Clear explanation of current MVP strengths and limitations.

Module 4 - Technology Intelligence
- Search/RAG-oriented research workflow, not homepage keyword scraping.
- Example research prompts.
- Live research call with source links.
- Persistent research history.
- Requires OpenAI API key with available API credits.

IMPORTANT
---------
The launcher now stops previous Workbench processes on ports 5173 and 8001-8004 before starting V3. This avoids the earlier issue where Vite silently selected another port while the browser reopened the old V1 website on port 5173.

Start
-----
Double-click: start_professional_web.bat
Then verify the top bar says: V3 - PRODUCT EXPERIENCE
